import concurrent.futures
import http.client
import json
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adapters import DemoAdapter
from server import make_handler
from store import Store, Conflict
from worker import Worker

CONFIG = dict(auto_enabled=False, max_retries=3, cooldown_seconds=15, min_confidence=.85, poll_seconds=3)


class StoreFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'test.sqlite3'
        self.store = Store(self.path, CONFIG)

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def port(self, port_id):
        return self.store.detail(port_id)['port']


class DashboardTests(StoreFixture):
    def test_manual_ignores_auto_switch_but_not_policy(self):
        job = self.store.enqueue('A05C11-P1')
        self.assertEqual(job['source'], 'MANUAL')
        self.assertEqual(self.port(job['port_id'])['status'], 'RETRYING')

    def test_auto_requires_switch_and_port_permission(self):
        with self.assertRaises(Conflict):
            self.store.enqueue('A05C11-P1', 'AUTO')
        self.store.update_config({'auto_enabled': True})
        self.store.review('A05C11-P1', 'ENVIRONMENT', '환경을 확인한 근거', False)
        with self.assertRaises(Conflict):
            self.store.enqueue('A05C11-P1', 'AUTO')

    def test_defect_unknown_offline_and_busy_are_blocked(self):
        for port_id in ('A13B01-P1', 'A13B02-P1', 'LSB01-P1', 'A05C11-P2'):
            with self.subTest(port=port_id), self.assertRaises(Conflict):
                self.store.enqueue(port_id)

    def test_cannot_approve_busy_port(self):
        with self.assertRaises(Conflict):
            self.store.review('A05C11-P2', 'ENVIRONMENT', '검토 근거', True)

    def test_duplicate_requests_are_atomic(self):
        def submit(_):
            try:
                return self.store.enqueue('A05C11-P1')['id']
            except Conflict:
                return None
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            accepted = [j for j in pool.map(submit, range(16)) if j]
        self.assertEqual(len(accepted), 1)
        self.assertEqual(self.port('A05C11-P1')['attempts'], 1)

    def test_launch_success_means_running_not_pass(self):
        job = self.store.enqueue('A05C11-P1')
        Worker(self.store, DemoAdapter(), stage_seconds=0).execute(job['id'])
        self.assertEqual(self.port('A05C11-P1')['status'], 'RUNNING')
        self.assertTrue(self.port('A05C11-P1')['busy'])
        self.assertEqual(self.store.state()['jobs'][0]['status'], 'SUCCEEDED')

    def test_launch_failure_needs_review_and_no_auto_loop(self):
        job = self.store.enqueue('A08B22-P1')
        Worker(self.store, DemoAdapter(), stage_seconds=0).execute(job['id'])
        p = self.port('A08B22-P1')
        self.assertEqual(p['status'], 'FAIL')
        self.assertEqual(p['attempts'], 2)
        self.assertFalse(p['reviewed'])
        self.assertFalse(p['auto_allowed'])
        with self.assertRaises(Conflict):
            self.store.enqueue(p['id'])

    def test_retry_limit_and_cooldown(self):
        self.store.update_config({'max_retries': 1})
        with self.assertRaises(Conflict):
            self.store.enqueue('A08B22-P1')
        job = self.store.enqueue('A05C11-P1')
        self.store.finish(job['id'], False, '데모 실패')
        self.store.review(job['port_id'], 'ENVIRONMENT', '환경 재확인 완료', True)
        self.store.update_config({'max_retries': 3})
        with self.assertRaisesRegex(Conflict, '간격'):
            self.store.enqueue(job['port_id'])

    def test_original_failure_is_immutable_on_review_and_retry(self):
        before = self.store.detail('A05C11-P1')['failures'][0]
        self.store.review('A05C11-P1', 'ENVIRONMENT', '새로운 담당자 검토 근거', True)
        job = self.store.enqueue('A05C11-P1')
        Worker(self.store, DemoAdapter(), stage_seconds=0).execute(job['id'])
        self.assertEqual(before, self.store.detail('A05C11-P1')['failures'][0])

    def test_new_failure_resets_attempts_and_preserves_old_evidence(self):
        job = self.store.enqueue('A05C11-P1')
        Worker(self.store, DemoAdapter(), stage_seconds=0).execute(job['id'])
        p = self.store.simulate_failure('A05C11-P1', 'UNKNOWN')
        self.assertEqual(p['attempts'], 0)
        self.assertFalse(p['reviewed'])
        self.assertEqual(len(self.store.detail(p['id'])['failures']), 2)
        self.assertEqual(len(self.store.detail(p['id'])['jobs']), 1)

    def test_restart_does_not_replay_uncertain_dispatch(self):
        job = self.store.enqueue('A05C11-P1')
        self.store.advance(job['id'], 'LAUNCHING', '실행 중단 상황')
        self.store.close()
        self.store = Store(self.path, CONFIG)
        p = self.port('A05C11-P1')
        self.assertEqual(p['status'], 'FAIL')
        self.assertFalse(p['reviewed'])
        self.assertIsNone(self.store.next_job())
        self.assertEqual(self.store.state()['jobs'][0]['status'], 'FAILED')

    def test_automatic_dispatch_executes_reviewed_candidates(self):
        self.store.update_config({'auto_enabled': True})
        worker = Worker(self.store, DemoAdapter(), stage_seconds=0)
        worker.start()
        # Event-based bounded waiting without a long fixed sleep.
        for _ in range(100):
            jobs = self.store.state()['jobs']
            if len(jobs) >= 3 and all(j['status'] in ('SUCCEEDED','FAILED') for j in jobs):
                break
            threading.Event().wait(.01)
        worker.stop()
        worker.join(timeout=2)
        jobs = self.store.state()['jobs']
        self.assertEqual({j['port_id'] for j in jobs}, {'A05C11-P1','A08B21-P1','A08B22-P1'})
        self.assertTrue(all(j['source'] == 'AUTO' for j in jobs))
        self.assertTrue(all(j['status'] in ('SUCCEEDED','FAILED') for j in jobs))

    def test_invalid_config_has_no_side_effect(self):
        for updates in ({'max_retries':True}, {'max_retries':-1}, {'min_confidence':2}, {'auto_enabled':'yes'}, {'unexpected':1}):
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                self.store.update_config(updates)
        self.assertEqual(self.store.state()['config'], CONFIG)

    def test_missing_preservation_and_reservation_block_submission(self):
        with self.store.lock, self.store.db:
            p=self.store._port('A05C11-P1')
            p.update(evidence_saved=False,reservation_ok=False)
            self.store._save_port(p)
        with self.assertRaisesRegex(Conflict, '예약.*보존'):
            self.store.enqueue(p['id'])


class HTTPTests(StoreFixture):
    def request(self, method, path, payload=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=2)
        body = json.dumps(payload) if payload is not None else None
        request_headers = dict(headers or {})
        if body:
            request_headers.setdefault('Content-Type','application/json')
        connection.request(method,path,body,request_headers)
        response=connection.getresponse()
        result=(response.status,response.read(),response.getheader('Content-Type'))
        connection.close()
        return result

    def setUp(self):
        super().setUp()
        self.server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(self.store))
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        super().tearDown()

    def test_http_state_static_and_mutation(self):
        self.assertEqual(self.request('GET','/')[0],200)
        self.assertEqual(self.request('GET','/app.js')[0],200)
        status,body,_=self.request('GET','/api/state')
        self.assertEqual(status,200)
        self.assertEqual(len(json.loads(body)['ports']),16)
        self.assertEqual(self.request('POST','/api/retry',{'port_id':'A05C11-P1'})[0],200)
        self.assertEqual(self.request('POST','/api/retry',{'port_id':'A05C11-P1'})[0],409)

    def test_cross_origin_rebinding_and_traversal_rejected(self):
        self.assertEqual(self.request('POST','/api/settings',{'auto_enabled':True},{'Origin':'http://evil.example'})[0],403)
        self.assertEqual(self.request('GET','/api/state',headers={'Host':'evil.example'})[0],403)
        self.assertEqual(self.request('GET','/../config.json')[0],404)
        self.assertFalse(self.store.state()['config']['auto_enabled'])

    def test_optional_authentication(self):
        self.server.RequestHandlerClass=make_handler(self.store,'test-token')
        self.assertEqual(self.request('GET','/api/state')[0],401)
        self.assertEqual(self.request('GET','/api/state',headers={'Authorization':'Bearer test-token'})[0],200)


if __name__ == '__main__':
    unittest.main()
