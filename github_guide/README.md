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
▸ 만약 VSCode등에서 적용이 안된 것 처럼 보이면 껐다키거나 Ctrl + Shift + P → "Reload Window" 입력 → 엔터
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
***
### ✏️여러가지 시나리오
#### ✔️ commit하고 push 했는데 되돌리고 싶을 때
```bash
git reset --hard HEAD~1
git push origin HEAD --force
```
#### ✔️ rebase 과정
```bash
# 1. 메인 브랜치로 이동
git checkout main

# 2. 원격에서 최신 상태 받아오기
git pull origin main

# 3. 작업 중이던 브랜치로 다시 이동
git checkout my_branch

# 4. 메인 브랜치를 기준으로 리베이스
git rebase main

# 5. 충돌이 있다면 수정 → add → rebase --continue
git add .
git rebase --continue

# 6. 리베이스 후엔 강제 push (원격 브랜치 업데이트) - rebase하면 커밋 해시가 바뀌기 때문
git push origin my_branch --force

# 7. GitHub에서 Pull Request 생성 🎉
```
▸ rebase는 **"내 브랜치에서 남의 브랜치를 기준으로 내 히스토리를 다시 쌓는 것"** 이므로 내 브랜치로 이동한 다음에 rebase 해야 한다.
#### ✔️ branch 관련 작업들
##### 1) 브랜치 생성 + 바로 이동
```bash
git checkout -b branch_name
```
▸ branch_name이라는 새 브랜치를 만들고, 그 브랜치로 즉시 이동한다.
##### 2) 브랜치 이동
```bash
git checkout branch_name
```
▸ 이미 존재하는 브랜치(branch_name)로 이동한다.
##### 3) 현재 브랜치 확인
```bash
git branch
```
▸ 현재 로컬에 존재하는 브랜치 목록 중 * 표시된 것이 현재 브랜치이다.

▸ -a 옵션 : 원격 브랜치를 포함한 전체 브랜치 확인 가능
##### 4) 원격 브랜치를 로컬로 가져오기
```bash
git checkout -b branch_name origin/branch_name
```
▸ GitHub 등 원격 저장소에 있는 브랜치를 내 로컬에서 branch_name으로 만들고 이동한다.
##### 5) 로컬 브랜치 삭제
```bash
git branch -d branch_name
```
##### 6) 원격 브랜치 삭제
```bash
git push origin --delete branch_name
```
##### 7) 브랜치 이름 변경
```bash
git branch -m branch_name new_branch_name
```
