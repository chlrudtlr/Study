"""Fail-closed retry policy shared by manual and automatic dispatch."""

def blockers(port, config, now):
    reasons = []
    if not port['online']:
        reasons.append('PC 연결 끊김')
    if not port['device_present']:
        reasons.append('SSD 미인식')
    if not port['reservation_ok']:
        reasons.append('장비 예약 확인 필요')
    if port['busy'] or port['status'] in ('RUNNING', 'RETRYING'):
        reasons.append('Port에서 TC 실행 중')
    if port['status'] != 'FAIL':
        reasons.append('재투입 대상 Fail 아님')
    if port['classification'] != 'ENVIRONMENT':
        reasons.append('환경성 불량으로 검토되지 않음')
    if not port['reviewed']:
        reasons.append('담당자 검토 필요')
    if not port['evidence_saved']:
        reasons.append('원본 Log / Dump 보존 확인 필요')
    if port['attempts'] >= config['max_retries']:
        reasons.append('최대 재투입 횟수 도달')
    if now - port['last_attempt'] < config['cooldown_seconds']:
        reasons.append('재투입 간격 대기 중')
    return reasons


def automatic_blockers(port, config, now):
    reasons = blockers(port, config, now)
    if not config['auto_enabled']:
        reasons.append('자동 재투입 꺼짐')
    if not port['auto_allowed']:
        reasons.append('이 Port의 자동 재투입 미허용')
    if port['confidence'] < config['min_confidence']:
        reasons.append('분석 신뢰도가 자동 재투입 기준 미달')
    return reasons
