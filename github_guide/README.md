## 📜GitHub 사용법 정리
### ✅ VScode 에서 GitHub연동하는 방법
#### ① Git 설치 여부 확인
▸ 터미널(cmd, PowerShell, bash 등)에서 Git이 설치 되어있는지 확인한다.
```bash
git --version
```
▸ 버전이 출력되면 Git이 정상적으로 설치된 것이고, 설치되어 있지 않다면 Git 공식 사이트에서 운영체제에 맞는 버전을 다운로드한다.
#### ② GitHub 계정과 로컬 Git 연동
▸ 아래 명령어를 입력하여 GitHub 사용자 정보를 등록한다.
```bash
git config --global user.name "username"
git config --global user.email "email@example.com"
```
▸ user.name은 GitHub ID

▸ user.email은 GitHub에 등록한 이메일 주소

#### ③ VS Code에서 GitHub 저장소 클론 만들기
```bash
git clone https://github.com/chlrudtlr/your-repo-name.git
cd your-repo-name
```
▸ 클론이란 원격 저장소의 내용을 그대로 복사하여 로컬 컴퓨터에 새로운 디렉터리를 생성하고 그 안에 원격 저장소의 파일들과 commit history를 가져오는 기능이다.
#### ④ Git 내용 가져오기
▸ 만약 클론이 이미 존재하고 깃허브 홈페이지에서 직접 수정한 사항을 로컬에 반영하고 싶은 경우 아래와 같은 명령어를 통해 적용할 수 있다.
```bash
git pull origin main
```
#### ⑤ 작업 방법
1) 파일을 vim으로 수정 또는 GUI로 열어서 작업
```bash
vi filename.cpp
```
```bash
code .
```
2) 변경사항 Git에 반영
```bash
git status     # 어떤 파일이 변경되었는지 확인
git add .      # 모든 변경 사항 스테이징
git commit -m "commit message"
git push       # GitHub로 반영
```
