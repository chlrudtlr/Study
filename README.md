## ✏️ Study </br>
### ✔️ Linux Terminal에서 명령어로 C++파일 Compile 방법 </br>
#### 1. C++파일 생성 및 작성
```bash
vi test.cpp
```
#### 2. Compile
```bash
g++ test.cpp -o test
```
• g++ : GNU C++ 컴파일러 (GCC의 C++ 버전)

• hello.cpp : 컴파일할 소스 파일

• -o hello : 컴파일 결과물을 hello라는 실행파일로 만들겠다는 뜻

#### 3. Run
```bash
./test
```
• ./hello는 현재 디렉토리에 있는 hello라는 실행파일을 실행하겠다는 의미 </br>

### ✔️ Linux Terminal에서 명령어로 C++파일 Compile 방법
#### 1. Makefile이란?
• 컴파일 명령어를 자동화해주는 스크립트 파일

• 파일 이름은 반드시 Makefile 또는 makefile

• make 명령어를 통해 간단히 컴파일 가능

#### 2. make Makefile Example
```bash
# Makefile

# 컴파일러 설정
CXX = g++
CXXFLAGS = -std=c++17 -Wall

# 타겟 이름
TARGET = test

# 소스 파일
SRC = test.cpp

# 기본 명령어 (make 실행 시 호출됨)
all: $(TARGET)

# 실행파일 만드는 규칙
$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

# 실행파일과 생성된 파일 삭제
clean:
	rm -f $(TARGET)
```

#### 3. Compile
```bash
make
```
• g++ -std=c++17 -Wall -o test test.cpp 명령어가 자동으로 실행

• test 실행파일이 생성

#### 4. Run
```bash
./test
```
#### 5. 실행파일 삭제
```bash
make clean
```
• test 실행파일이 삭제
