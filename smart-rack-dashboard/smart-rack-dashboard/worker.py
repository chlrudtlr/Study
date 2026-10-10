"""Single dispatcher; port-level duplicate prevention lives in SQLite."""
import threading
from store import Conflict


class Worker(threading.Thread):
    def __init__(self, store, adapter, stage_seconds=1.6):
        super().__init__(name='retry-dispatcher', daemon=True)
        self.store, self.adapter = store, adapter
        self.stage_seconds = stage_seconds
        self.stop_event = threading.Event()

    def execute(self, job_id):
        try:
            port = self.store.advance(job_id, 'CHECKING', '예약·Port 점유 확인')
            check = self.adapter.preflight(port)
            if not check.ok:
                self.store.finish(job_id, False, check.message)
                return
            if self.stop_event.wait(self.stage_seconds):
                return
            for stage, message in self.adapter.stages[1:]:
                port = self.store.advance(job_id, stage, message)
                if self.stop_event.wait(self.stage_seconds):
                    return
            # Fresh check immediately before dispatch.
            check = self.adapter.preflight(port)
            if not check.ok:
                self.store.finish(job_id, False, check.message)
                return
            result = self.adapter.launch(port, job_id)
            self.store.finish(job_id, result.ok, result.message)
        except Exception as exc:
            self.store.finish(job_id, False, f'어댑터 실행 실패 ({type(exc).__name__}) · 담당자 확인 필요')

    def run(self):
        while not self.stop_event.is_set():
            state = self.store.state()
            if state['config']['auto_enabled']:
                for port in state['ports']:
                    if not port['auto_blockers']:
                        try:
                            self.store.enqueue(port['id'], 'AUTO')
                        except Conflict:
                            pass
            job_id = self.store.next_job()
            if job_id:
                self.execute(job_id)
            else:
                self.stop_event.wait(1)

    def stop(self):
        self.stop_event.set()
