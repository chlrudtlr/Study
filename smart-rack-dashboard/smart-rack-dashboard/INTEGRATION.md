# 실제 Rack / 기존 AURA 연동 가이드

현재 패키지는 완성된 **로컬 Dashboard 데모**입니다. 실제 장비 실행기는 포함하지 않습니다.
기존 watcher·분석 결과·SUP 예약·재투입 실행기를 연결할 때 사용할 경계를 설명합니다.

## 1. 권장 연결 구조

| 구성 | 담당 |
| --- | --- |
| 평가 watcher | 현재 TC와 평가 결과, 신규 Fail, Port 점유 상태 수집 |
| 분석기 | 원인 분류, 신뢰도, 검토할 근거 생성 |
| 장비 상태 수집기 | Online, SSD 인식, 예약 유효 여부와 관측 시각 수집 |
| Dashboard API | 조회, 담당자 검토, 정책, 재투입 등록 요청 |
| 재투입 worker | 실행 직전 재검증, 배타적 예약, 장비 준비, TC 시작 확인 |
| 기존 원본 저장소 | 원본 Log / Dump와 hash, 평가 실행 ID 보존 |

기존 AURA Flask / FastAPI 서버가 있다면 `static` UI를 이식하고 API를 기존 저장소에 맞추는 방식이 자연스럽습니다.
현재 `server.py`는 다른 프레임워크 없이 화면을 실행해 보기 위한 서버입니다.

## 2. UI API 계약

모든 POST는 `Content-Type: application/json`입니다.
정책 위반 / 상태 충돌은 409, 입력 오류는 400, 토큰이 필요한 서버에서 인증 실패는 401입니다.

| Method | Path | 내용 |
| --- | --- | --- |
| GET | `/api/state` | Port, 최신 100개 조치, 최근 60개 이벤트, 설정, 전체 조치 결과 집계 |
| GET | `/api/ports/{port_id}` | 해당 Port 상세, 전체 조치, 원본 Fail 기록 |
| POST | `/api/retry` | `{"port_id":"A05C11-P1"}` |
| POST | `/api/review` | `{"port_id":"A05C11-P1","classification":"ENVIRONMENT","note":"검토 근거","auto_allowed":false}` |
| POST | `/api/settings` | `auto_enabled`, `max_retries`, `cooldown_seconds`, `min_confidence` 중 수정할 값 |
| POST | `/api/demo/failure` | 데모 전용. `{"port_id":"A05C11-P2","scenario":"UNKNOWN"}` |

`/api/demo/failure`는 실제 운영에 노출하지 마세요.
실제 Fail 수신 endpoint는 이 패키지에 구현되어 있지 않습니다.
watcher 연동 시 신규 평가 실행 ID로 중복 수신을 제거하고 저장소 트랜잭션에서 생성하세요.

### 상태 모델 예시

```json
{
  "id": "A05C11-P1",
  "rack": "A05C",
  "pc": "A05C11",
  "port": 1,
  "tc": "essential_reset",
  "status": "FAIL",
  "online": true,
  "device_present": true,
  "reservation_ok": true,
  "busy": false,
  "classification": "ENVIRONMENT",
  "confidence": 0.94,
  "cause": "SSH 연결 중 일시적 통신 실패",
  "evidence": "검토할 원본 로그 발췌 및 장비 상태",
  "evidence_saved": true,
  "reviewed": true,
  "auto_allowed": true,
  "attempts": 0,
  "last_attempt": 0,
  "issue_id": "UNIQUE-FAIL-ID"
}
```

`status`: RUNNING / PASS / FAIL / RETRYING / IDLE.
`classification`: ENVIRONMENT / GENUINE / UNKNOWN / NONE.
시간은 Unix epoch 초입니다. 화면에서는 브라우저의 현지 시간으로 표시합니다.

실제 watcher는 장비 상태의 **관측 시각·유효기간**도 저장하고 오래된 상태로 실행하지 않아야 합니다.
이 데모의 온라인·예약·보존 flag는 모의 데이터이며 실제 실행 허가 근거로 사용할 수 없습니다.

## 3. 어댑터 교체

`adapters.py`의 `DemoAdapter`와 같은 인터페이스를 구현하고 `server.py`의 worker 생성부에 전달합니다.
실제 어댑터 예시 코드는 의도적으로 포함하지 않았습니다. 장비 API·권한·명령 규약이 확인된 뒤 작성해야 합니다.

| 메서드 / 필드 | 계약 |
| --- | --- |
| `mode` | 실제 어댑터는 DEMO와 구분되는 이름 |
| `stages` | worker가 기록할 단계 코드와 설명 |
| `preflight(port)` | 장비·예약·Port 실제 상태를 다시 확인하고 `CheckResult(ok, message)` 반환 |
| `launch(port, job_id)` | 해당 TC 실행 시작을 확인하고 결과 반환. `job_id`로 멱등성 보장 |

연동 시 `Store.state()`의 `mode`, UI의 DEMO 문구도 실제 연결 상태에 맞게 바꾸세요.
단순히 표시만 LIVE로 변경해 실제 연결처럼 보이게 하지 마세요.

실제 실행에는 추가 계약이 필요합니다.

1. 다른 watcher / 사용자가 같은 Port에 실행할 수 있으므로 **장비 측 배타 예약**을 획득해야 합니다. 현재 SQLite 잠금은 이 Dashboard 안의 중복만 차단합니다.
2. 예약 사용자·유효시간·PC / Port / Bus / SSD 식별자를 확인하세요. 예약 확인과 실행 사이의 경쟁도 처리해야 합니다.
3. 실패 시 원본 로그·덤프를 실제로 보존하고 완료 확인 후 `evidence_saved=true`를 설정하세요.
4. Remote launch에 `job_id`를 전달하고 같은 ID를 다시 받아도 TC를 중복 시작하지 않게 해야 합니다.
5. 모든 외부 호출에 timeout을 두세요. timeout 후에는 실제 시작 여부가 불명확할 수 있으므로 확인 없이 재투입하지 마세요.
6. `launch()` 성공은 평가 시작을 의미합니다. Pass / Fail은 watcher가 별도로 반영해야 합니다.
7. watcher가 실행 중 장비 상태를 바꾸는 경우 단계마다 최신 snapshot을 가져와 재검증하세요. 현재 데모는 외부 상태 수집기가 없습니다.
8. PMU power cycle은 범용 재투입 과정에 기본 포함하지 않았습니다. 필요한 시나리오에서 승인된 절차와 실패 복구 계약을 연결하세요.

## 4. 데이터·권한·배포

- `data/dashboard.sqlite3`는 이 패키지의 데모 저장소입니다. 운영에서는 기존 AURA DB와 통합해 상태를 이중 관리하지 않는 것이 좋습니다.
- 원본 Fail 스냅샷은 수정하지 않고 검토·재투입은 별도 레코드에 남깁니다.
- 현재 UI 이력과 CSV는 최신 100개 조치를 대상으로 합니다. Port 상세와 DB에는 이전 전체 이력이 남습니다. 운영 규모에는 페이지네이션·기간 조회를 추가하세요.
- 이벤트에는 시각·Port·조치 ID가 있으나 사용자별 인증은 없습니다. 실제 검토자·실행 요청자 식별자를 SSO 세션에서 기록하세요.
- 공용 API 토큰은 데모 접근 제어입니다. 실제 운영은 사내 인증과 Rack / Port별 사용 권한을 서버에서 검사해야 합니다.
- 배포 시 현재 데모 HTTP 서버 대신 기존 서비스 또는 production WSGI / ASGI 서버와 TLS proxy를 사용하세요.
- worker는 한 프로세스·한 인스턴스를 전제로 합니다. 여러 서버에 배포하려면 분산 lease / job claim, 결과 불명확 상태, 멱등 실행 계약이 필요합니다.

## 5. 기본 정책

`config.json`의 기본값은 자동 OFF / 최대 3회 / 간격 15초 / 최소 신뢰도 85%입니다.
설정은 최초 데이터 생성에만 적용됩니다. 이후에는 UI에서 변경합니다.
AI의 confidence는 운영 데이터로 검증한 뒤 사용하고, 담당자 검토 및 장비 조건은 서버의 명시적 정책으로 유지하세요.
