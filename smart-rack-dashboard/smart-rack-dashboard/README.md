# AURA · Smart Rack Dashboard

원격 Rack의 SSD TC 평가 현황과 자동 재투입을 관리하는 **실행 가능한 로컬 데모**입니다.
첨부 시안의 상단 Rack 현황 / 하단 재투입 목록 구조를 바탕으로 만들었습니다.

**이 패키지는 실제 Rack에 연결하지 않습니다.** 장비 상태, 분석 분류·신뢰도,
Log / Dump 경로는 모두 예시입니다. 재투입은 Python의 모의 장비 어댑터가 수행합니다.
AI 모델 호출, SSH, SUP 예약, PMU 제어, NVMe 명령 실행은 포함하지 않습니다.

## 1. 바로 실행하기

Python **3.10 이상**, 최신 Chrome / Edge / Firefox가 필요합니다.
외부 Python 패키지, Node.js 설치, npm 빌드, 인터넷 연결은 필요하지 않습니다.

### Windows

ZIP 압축을 풀고 `smart-rack-dashboard` 폴더에서 `start.bat`를 실행하세요.
또는 터미널에서 다음 명령을 입력합니다.

```powershell
cd .\smart-rack-dashboard
py -3 server.py
```

Python 런처 `py`가 없고 `python`이 설치되어 있다면 `python server.py`로 실행하세요.

### Linux

```bash
cd smart-rack-dashboard
bash start.sh
```

브라우저에서 **http://127.0.0.1:8080** 에 접속합니다. 종료는 터미널에서 `Ctrl+C`입니다.
`static/index.html`을 더블클릭하지 마세요. Dashboard는 서버 API를 사용합니다.

8080 포트를 이미 사용하고 있다면:

```bash
python3 server.py --port 8081
```

접속 주소도 `http://127.0.0.1:8081`로 변경합니다.

### SSH로 연결한 서버에서 실행할 경우

서버에서 위와 같이 실행하고, 내 PC에서 SSH 포트 포워딩을 열면 됩니다.
VSCode Remote SSH의 **PORTS** 탭에서 8080을 포워딩해도 됩니다.

```bash
ssh -L 18080:127.0.0.1:8080 USER@SERVER
```

내 PC 브라우저에서 `http://127.0.0.1:18080`으로 접속합니다.
기본 서버는 로컬 주소에만 바인딩합니다.

## 2. 화면 구성

| 메뉴 | 주요 기능 |
| --- | --- |
| Dashboard | 전체 Port / Running / Fail / 재투입 가능 / 재투입 시작 성공률, 자동 ON/OFF, Rack별 현황, 최근 활동, Fail 분포 |
| 재투입 관리 | Rack·PC·Port·TC·실패 원인, 모의 분석 근거, 검토 상태, 횟수, 최신 조치, 수동 재투입 |
| 실행 이력 | Port별 최신 조치, 이전 이력 펼치기, 실행 단계, 최근 100건 CSV 다운로드 |
| 자동화 정책 | 최대 횟수, 재투입 간격, 자동 실행 최소 신뢰도 |
| Port 상세 | 장비 상태, 차단 사유, 담당자 검토, Port별 전체 이력, 원본 Fail 스냅샷 |

- A05C / A08B / A13B / LSB, Rack마다 PC 2대 × Port 2개 = **총 16 Port** 예시입니다.
- 3초마다 서버 상태를 갱신합니다. 연결 실패 시 마지막 수신 상태와 오류를 표시합니다.
- Port 상세 창은 검토 입력을 보호하기 위해 자동으로 덮어쓰지 않습니다. 창 오른쪽 위 새로고침 버튼으로 갱신합니다.
- 상태는 글자와 색을 함께 사용하고, 좁은 화면에서는 카드가 재배치됩니다.
- 기본 화면은 자동 재투입 **OFF**입니다.
- 성공률은 **TC 재투입 시작 성공률**입니다. TC 평가 Pass율과 다릅니다.
- 재투입 시작 성공 시 `Running`으로 변경합니다. 실제 평가 완료 결과는 이 데모에서 자동 생성하지 않습니다.

## 3. 2분 데모 순서

1. Dashboard의 `A05C11 / P1`을 클릭해 원인, 필수 조건과 원본 Fail을 확인합니다.
2. `수동 재투입`을 누르면 `Retrying`으로 바뀝니다.
3. 약 5초 후 모의 시작이 성공하면 `Running`으로 바뀝니다.
4. 실행 이력에서 단계와 성공 기록을 펼쳐봅니다.
5. Dashboard의 자동 재투입을 ON으로 바꿉니다. 검토 완료·자동 허용·장비 조건을 만족한 Fail만 자동 등록됩니다.
6. `A08B22-P1 / essential_fw_update`는 예시로 두 번째 재투입 시작이 실패합니다. 담당자 재검토를 요구하며 자동 반복하지 않습니다.
7. `Fail 시뮬레이션`에서 Running / Pass / Idle Port에 환경성 Fail을 생성합니다.
8. 상세에서 검토 근거를 입력하고 환경성으로 저장합니다. 자동 허용을 체크하면 전역 ON 및 신뢰도 조건을 만족할 때 자동 실행합니다.
9. 실제 Defect 의심, 판단 불가, Offline Port는 그대로는 재투입하지 않습니다. 상세에서 차단 사유를 확인합니다.

자동 ON 상태에서는 검토를 저장하는 즉시 신규 조치가 등록될 수 있습니다.
수동 버튼을 시험하려면 먼저 자동 OFF로 전환하세요.

## 4. 재투입 판단과 상태 관리

수동·자동 모두 `policy.py`의 공통 조건을 검사합니다.

| 조건 | 수동 | 자동 |
| --- | --- | --- |
| 현재 Fail이며 PC Online / SSD 인식 / 예약 유효 / Port 비점유 | 필수 | 필수 |
| 담당자가 환경성 불량으로 검토 완료 | 필수 | 필수 |
| 원본 Log / Dump 보존 확인 | 필수 | 필수 |
| Fail당 최대 횟수, 같은 Fail의 재투입 간격 | 적용 | 적용 |
| 전역 자동 ON | 무관 | 필수 |
| 해당 Fail 자동 허용 | 무관 | 필수 |
| 최소 분석 신뢰도 | 무관 | 필수 |

`분석 분류·신뢰도`와 `재투입 허용`을 분리했습니다.
신뢰도만 높다는 이유로 실제 Defect 의심이나 미검토 Fail을 실행하지 않습니다.
담당자가 분류를 변경할 때는 검토 근거를 기록합니다. 원본 분류는 별도로 유지합니다.

실행 단계: `QUEUED → CHECKING → PREPARING → LAUNCHING → SUCCEEDED / FAILED`

- Port 잠금과 조치 생성은 SQLite 트랜잭션에서 함께 처리합니다.
- 활성 조치는 Port당 1개만 허용하는 SQLite unique index로 중복 요청을 방지합니다.
- 예약·장비 상태를 어댑터에서 다시 확인한 뒤 시작합니다. 데모에서는 모의 상태를 확인합니다.
- 시작 실패 시 `Fail`로 복귀하고 자동 허용과 검토 완료 상태를 해제합니다.
- 새 Fail 생성은 새 `issue_id`를 사용하고 횟수를 0으로 초기화합니다.
- 재투입 횟수는 시작 요청이 아니라 **조치 등록 시점**에 증가합니다.
- 자동 OFF는 **신규 자동 등록만** 중지합니다. 이미 등록한 수동·자동 조치는 계속 실행합니다.
- 서버 재시작 시 중단된 조치는 실패 / 확인 필요로 남깁니다. 자동으로 재실행하지 않습니다.

## 5. 파일 구성

| 파일 | 역할 |
| --- | --- |
| `server.py` | 정적 파일 및 HTTP JSON API 제공 |
| `store.py` | SQLite, Port 상태, 원본 Fail, 검토 기록, 조치 이력 |
| `policy.py` | 공통 재투입 조건 및 자동 실행 조건 |
| `worker.py` | 자동 후보 등록과 단일 조치 실행 worker |
| `adapters.py` | 모의 장비 어댑터 / 실제 연동 경계 |
| `seed.py` | 최초 데모 장비 데이터 |
| `config.json` | 최초 DB 생성 시 적용되는 기본 설정 |
| `static/index.html` | Dashboard UI 구조 |
| `static/styles.css` | 반응형 스타일 |
| `static/app.js` | 화면 갱신·필터·상세·검토·재투입·CSV |
| `tests/test_dashboard.py` | 정책·동시 요청·상태 전이·이력·HTTP 검증 |
| `INTEGRATION.md` | 기존 AURA / 실제 Rack 연동 가이드 |

운영 데이터는 첫 실행 시 `data/dashboard.sqlite3`에 생성됩니다.
정책 변경은 DB에 저장됩니다. 기존 DB가 있으면 `config.json`을 다시 읽어 덮어쓰지 않습니다.
원본 Fail은 최초 스냅샷, 조치는 시도별 기록, 검토·단계는 이벤트에 남습니다.
실제 Log / Dump 바이트를 저장하는 시스템은 아니며 해당 연동은 별도로 구현해야 합니다.

초기 데모로 돌아가려면 서버를 종료한 뒤 `data` 폴더를 삭제하고 다시 실행하세요.
이 작업은 데모 상태와 이력을 초기화합니다.

## 6. 테스트

```bash
python3 -m unittest discover -s tests -v
```

Windows에서는 `py -3 -m unittest discover -s tests -v`입니다.
추가 의존성 없이 **17개 테스트**를 실행합니다.
중복 등록, 필수 조건, 자동 허용, 시작 성공과 Pass 구분, 시작 실패 후 재검토,
원본 보존, 새 Fail 초기화, 재시작 시 불확실한 작업 재실행 방지, API와 요청 접근 제어를 확인합니다.

Python 실행·API·정책 테스트 및 JavaScript 문법 검사를 완료했습니다.
실제 브라우저에서의 렌더링·클릭 검증과 실제 장비 연동 검증은 수행하지 않았습니다.

## 7. 다른 PC에서 데모에 접속하려면

다른 PC에 노출할 때는 `AURA_API_TOKEN`을 24자 이상으로 설정해야 합니다.
토큰은 브라우저 접속 시 입력하며 현재 탭 메모리에만 유지됩니다.

```bash
export AURA_API_TOKEN='REPLACE_WITH_A_RANDOM_SECRET_AT_LEAST_24_CHARS'
python3 server.py --host 0.0.0.0 --port 8080
```

이 서버는 Python 표준 라이브러리의 데모 HTTP 서버입니다.
사내 운영 배포는 기존 AURA 서버 또는 인증·TLS를 갖춘 reverse proxy 뒤에 통합하세요.
실제 Rack 연동, 계정별 권한, 예약 원자성, 장비 상태 수집, 작업 timeout,
원본 로그 보관은 `INTEGRATION.md`의 계약에 맞춰 추가해야 합니다.
