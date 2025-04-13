## 📜GitHub 사용법 정리
✅ **VScode 에서 GitHub연동하는 방법**

① Git 설치 여부 확인
터미널(cmd, PowerShell, bash 등)에서 Git이 설치 되어있는지 확인한다.
```bash
git --version
```
버전이 출력되면 Git이 정상적으로 설치된 것이고, 설치되어 있지 않다면 Git 공식 사이트에서 운영체제에 맞는 버전을 다운로드한다.

② GitHub 계정과 로컬 Git 연동
아래 명령어를 입력하여 GitHub 사용자 정보를 등록한다.
```bash
git config --global user.name "username"
git config --global user.email "email@example.com"
```
