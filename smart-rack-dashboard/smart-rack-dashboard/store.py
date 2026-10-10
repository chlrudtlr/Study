"""Transactional SQLite state and append-only attempt/event history."""
import json
import sqlite3
import threading
import time
import uuid

from policy import blockers, automatic_blockers
from seed import sample_ports


class Conflict(Exception):
    pass


class Store:
    def __init__(self, database, initial_config):
        self.lock = threading.RLock()
        self.db = sqlite3.connect(str(database), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS ports (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY, port_id TEXT NOT NULL, issue_id TEXT NOT NULL,
                status TEXT NOT NULL, payload TEXT NOT NULL);
            CREATE UNIQUE INDEX IF NOT EXISTS one_active_job ON jobs(port_id)
                WHERE status IN ('QUEUED','CHECKING','PREPARING','LAUNCHING');
            CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS failures (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        ''')
        with self.lock, self.db:
            if not self.db.execute('SELECT 1 FROM settings').fetchone():
                self.db.execute('INSERT INTO settings VALUES (1,?)', (json.dumps(initial_config),))
            if not self.db.execute('SELECT 1 FROM ports').fetchone():
                for port in sample_ports():
                    self._save_port(port)
                    if port['issue_id']:
                        self._save_failure(port)
                self._event('SYSTEM', '데모 데이터 준비 완료 · 실제 장비 연결 없음')
            # Never replay jobs whose dispatch result may be uncertain after restart.
            for row in self.db.execute("SELECT payload FROM jobs WHERE status IN ('QUEUED','CHECKING','PREPARING','LAUNCHING')").fetchall():
                job = json.loads(row[0])
                job.update(status='FAILED', message='서버 재시작: 실행 결과 확인 필요', finished=time.time())
                self._save_job(job)
                port = self._port(job['port_id'])
                port.update(status='FAIL', busy=False, reviewed=False, auto_allowed=False)
                self._save_port(port)
                self._event('WARNING', '서버 재시작으로 중단된 조치: 담당자 확인 필요', port['id'], job['id'])

    def _port(self, port_id):
        row = self.db.execute('SELECT payload FROM ports WHERE id=?', (port_id,)).fetchone()
        if row is None:
            raise KeyError('Port를 찾을 수 없습니다.')
        return json.loads(row[0])

    def _config(self):
        return json.loads(self.db.execute('SELECT payload FROM settings WHERE id=1').fetchone()[0])

    def _save_port(self, port):
        self.db.execute('INSERT OR REPLACE INTO ports VALUES (?,?)', (port['id'], json.dumps(port, ensure_ascii=False)))

    def _save_job(self, job):
        self.db.execute('INSERT OR REPLACE INTO jobs VALUES (?,?,?,?,?)',
                        (job['id'], job['port_id'], job['issue_id'], job['status'], json.dumps(job, ensure_ascii=False)))

    def _save_failure(self, port):
        # Original snapshots are immutable, even after review or retry.
        self.db.execute('INSERT INTO failures VALUES (?,?)', (port['issue_id'], json.dumps(port, ensure_ascii=False)))

    def _event(self, kind, message, port_id='', job_id=''):
        event = dict(time=time.time(), kind=kind, message=message, port_id=port_id, job_id=job_id)
        self.db.execute('INSERT INTO events(payload) VALUES (?)', (json.dumps(event, ensure_ascii=False),))

    def state(self):
        with self.lock:
            config = self._config()
            ports = [json.loads(r[0]) for r in self.db.execute('SELECT payload FROM ports ORDER BY id')]
            jobs = [json.loads(r[0]) for r in self.db.execute('SELECT payload FROM jobs ORDER BY rowid DESC LIMIT 100')]
            events = [json.loads(r[0]) for r in self.db.execute('SELECT payload FROM events ORDER BY id DESC LIMIT 60')]
            for port in ports:
                port['blockers'] = blockers(port, config, time.time())
                port['auto_blockers'] = automatic_blockers(port, config, time.time())
            totals = dict(self.db.execute('SELECT status, COUNT(*) FROM jobs GROUP BY status').fetchall())
            return dict(mode='DEMO', ports=ports, jobs=jobs, events=events, config=config,
                        job_totals=totals, server_time=time.time())

    def detail(self, port_id):
        with self.lock:
            port = self._port(port_id)
            config = self._config()
            port['blockers'] = blockers(port, config, time.time())
            port['auto_blockers'] = automatic_blockers(port, config, time.time())
            failures = [json.loads(r[0]) for r in self.db.execute('SELECT payload FROM failures ORDER BY rowid DESC')
                        if json.loads(r[0])['id'] == port_id]
            jobs = [json.loads(r[0]) for r in self.db.execute('SELECT payload FROM jobs WHERE port_id=? ORDER BY rowid DESC', (port_id,))]
            return dict(port=port, failures=failures, jobs=jobs)

    def enqueue(self, port_id, source='MANUAL'):
        with self.lock, self.db:
            port = self._port(port_id)
            config = self._config()
            checks = automatic_blockers if source == 'AUTO' else blockers
            reasons = checks(port, config, time.time())
            if reasons:
                raise Conflict(' · '.join(reasons))
            now = time.time()
            job = dict(id=uuid.uuid4().hex, port_id=port_id, issue_id=port['issue_id'],
                       rack=port['rack'], pc=port['pc'], port=port['port'], tc=port['tc'],
                       source=source, status='QUEUED', created=now, finished=None,
                       attempt=port['attempts'] + 1, message='실행 대기', stages=[])
            self._save_job(job)
            port.update(status='RETRYING', busy=True, attempts=job['attempt'], last_attempt=now, updated=now)
            self._save_port(port)
            self._event('RETRY', f'{"자동" if source == "AUTO" else "수동"} 재투입 등록 · {job["attempt"]}회차', port_id, job['id'])
            return job

    def advance(self, job_id, status, message):
        with self.lock, self.db:
            row = self.db.execute('SELECT payload FROM jobs WHERE id=?', (job_id,)).fetchone()
            if not row:
                raise KeyError('조치를 찾을 수 없습니다.')
            job = json.loads(row[0])
            job.update(status=status, message=message)
            job['stages'].append(dict(time=time.time(), status=status, message=message))
            self._save_job(job)
            self._event('STEP', message, job['port_id'], job_id)
            return self._port(job['port_id'])

    def finish(self, job_id, ok, message):
        with self.lock, self.db:
            job = json.loads(self.db.execute('SELECT payload FROM jobs WHERE id=?', (job_id,)).fetchone()[0])
            job.update(status='SUCCEEDED' if ok else 'FAILED', message=message, finished=time.time())
            self._save_job(job)
            port = self._port(job['port_id'])
            port.update(status='RUNNING' if ok else 'FAIL', busy=bool(ok), updated=time.time())
            if not ok:
                # A launch failure needs review rather than an unattended loop.
                port.update(reviewed=False, auto_allowed=False)
            self._save_port(port)
            self._event('SUCCESS' if ok else 'ERROR', message, port['id'], job_id)

    def next_job(self):
        with self.lock:
            row = self.db.execute("SELECT id FROM jobs WHERE status='QUEUED' ORDER BY rowid LIMIT 1").fetchone()
            return row[0] if row else None

    def update_config(self, updates):
        allowed = {'auto_enabled', 'max_retries', 'cooldown_seconds', 'min_confidence'}
        if set(updates) - allowed:
            raise ValueError('지원하지 않는 설정입니다.')
        with self.lock, self.db:
            config = self._config()
            config.update(updates)
            if type(config['auto_enabled']) is not bool:
                raise ValueError('auto_enabled는 boolean이어야 합니다.')
            for key, lo, hi in [('max_retries', 1, 10), ('cooldown_seconds', 0, 3600)]:
                if type(config[key]) is not int or not lo <= config[key] <= hi:
                    raise ValueError(f'{key}: {lo}~{hi} 정수가 필요합니다.')
            if type(config['min_confidence']) not in (int, float) or not 0 <= config['min_confidence'] <= 1:
                raise ValueError('min_confidence: 0~1 숫자가 필요합니다.')
            self.db.execute('UPDATE settings SET payload=? WHERE id=1', (json.dumps(config),))
            self._event('POLICY', '재투입 정책 변경 · 자동 ' + ('ON' if config['auto_enabled'] else 'OFF'))
            return config

    def review(self, port_id, classification, note, auto_allowed):
        if classification not in ('ENVIRONMENT', 'GENUINE', 'UNKNOWN'):
            raise ValueError('분류가 올바르지 않습니다.')
        if not isinstance(note, str) or not 3 <= len(note.strip()) <= 1000:
            raise ValueError('검토 근거를 3~1000자로 입력하세요.')
        if type(auto_allowed) is not bool:
            raise ValueError('auto_allowed는 boolean이어야 합니다.')
        with self.lock, self.db:
            port = self._port(port_id)
            if port['busy'] or port['status'] != 'FAIL':
                raise Conflict('Fail 상태에서만 검토할 수 있습니다.')
            port.update(classification=classification, reviewed=True,
                        review_note=note.strip(), auto_allowed=auto_allowed and classification == 'ENVIRONMENT', updated=time.time())
            self._save_port(port)
            self._event('REVIEW', f'담당자 검토: {classification} · {note.strip()}', port_id)
            return port

    def simulate_failure(self, port_id, scenario):
        scenarios = {
            'ENVIRONMENT': ('TC 런처 연결 중 일시적 통신 실패', .92),
            'GENUINE': ('Random Read UECC · 실제 Defect 의심', .96),
            'UNKNOWN': ('NVMe Timeout · 원인 미확정', .58),
        }
        if scenario not in scenarios:
            raise ValueError('지원하지 않는 데모 시나리오입니다.')
        with self.lock, self.db:
            port = self._port(port_id)
            if port['status'] in ('FAIL', 'RETRYING'):
                raise Conflict('새 Fail은 Running / Pass / Idle Port에 생성하세요.')
            cause, confidence = scenarios[scenario]
            port.update(status='FAIL', busy=False, classification=scenario, confidence=confidence,
                        cause=cause, evidence=f'[DEMO] {cause}\n이 분석은 시연용 예시입니다.',
                        issue_id='DEMO-' + uuid.uuid4().hex[:12], attempts=0, last_attempt=0,
                        reviewed=False, auto_allowed=False, review_note='', updated=time.time(),
                        log_path=f'demo/logs/{port_id}/original.log', dump_path=f'demo/dumps/{port_id}/original.bin')
            self._save_port(port)
            self._save_failure(port)
            self._event('FAIL', '새 모의 Fail 감지: ' + cause, port_id)
            return port

    def close(self):
        with self.lock:
            self.db.close()
