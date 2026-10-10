"""Synthetic examples; these records do not describe any actual equipment."""
import time


def sample_ports():
    layout = {
        'A05C': ['A05C11', 'A05C12'],
        'A08B': ['A08B21', 'A08B22'],
        'A13B': ['A13B01', 'A13B02'],
        'LSB': ['LSB01', 'LSB02'],
    }
    tcs = ['essential_reset', 'essential_nested_reset', 'essential_fw_update', 'essential_gc']
    rows = []
    for rack, pcs in layout.items():
        for pc in pcs:
            for n in (1, 2):
                i = len(rows)
                rows.append(dict(
                    id=f'{pc}-P{n}', rack=rack, pc=pc, port=n,
                    tc=tcs[i % len(tcs)], model=['PM9M1', 'BM9K1'][i % 2],
                    fw='DEMO-001', owner='평가 담당자', status='RUNNING',
                    online=True, device_present=True, reservation_ok=True,
                    busy=True, classification='NONE', confidence=0.0,
                    cause='', evidence='', log_path='', dump_path='',
                    reviewed=False, evidence_saved=True, auto_allowed=False,
                    attempts=0, last_attempt=0, issue_id='',
                    updated=time.time() - i * 73,
                ))
    def fail(i, kind, cause, confidence, reviewed=False, **extra):
        p = rows[i]
        p.update(status='FAIL', busy=False, classification=kind, cause=cause,
                 confidence=confidence, reviewed=reviewed, auto_allowed=reviewed,
                 issue_id=f'DEMO-FAIL-{i+1:03}',
                 evidence=f'[DEMO] {cause}\n장비 진단 결과와 TC 로그를 함께 검토해야 합니다.',
                 log_path=f'demo/logs/{p["id"]}/original.log',
                 dump_path=f'demo/dumps/{p["id"]}/original.bin', **extra)
    fail(0, 'ENVIRONMENT', 'SSH 연결 중 일시적 통신 실패', .94, True)
    fail(4, 'ENVIRONMENT', 'TC 런처 시작 응답 시간 초과', .91, True)
    fail(6, 'ENVIRONMENT', 'TC 런처 세션 종료', .89, True, attempts=1)
    fail(8, 'GENUINE', 'Random Read UECC · Media Error 증가', .97)
    fail(10, 'UNKNOWN', 'Admin Command Timeout · 원인 미확정', .62)
    fail(12, 'ENVIRONMENT', 'SSH 연결 실패 · PC 응답 없음', .93, True,
         online=False, device_present=False)
    rows[2].update(status='PASS', busy=False)
    rows[11].update(status='PASS', busy=False)
    rows[15].update(status='IDLE', busy=False)
    return rows
