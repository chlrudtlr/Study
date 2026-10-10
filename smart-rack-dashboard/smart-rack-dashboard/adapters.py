"""Equipment integration boundary. This package ships a simulator only."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    message: str


class DemoAdapter:
    mode = 'DEMO'
    # Deliberately deterministic; second retry of this TC fails in the demo.
    stages = (
        ('CHECKING', '예약·Port 점유 확인'),
        ('PREPARING', 'SSD 인식·원본 Log 보존 확인'),
        ('LAUNCHING', 'TC 재투입 요청'),
    )

    def preflight(self, port):
        ok = bool(port['online'] and port['device_present'] and port['reservation_ok'])
        return CheckResult(ok, '모의 장비 상태 확인 완료' if ok else '모의 장비 상태 확인 실패')

    def launch(self, port, job_id):
        """Return submission acceptance, NOT the final TC Pass/Fail."""
        if port['tc'] == 'essential_fw_update' and port['attempts'] >= 2:
            return CheckResult(False, '모의 실행: TC 시작 응답 시간 초과')
        return CheckResult(True, '모의 실행: TC 시작 확인 완료 (평가 결과는 Running)')


# A real adapter must perform fresh reservation/device/TC checks immediately
# before launch, use job_id as an idempotency key and enforce equipment-side
# exclusive ownership. Do not implement remote shell operations in HTTP routes.
