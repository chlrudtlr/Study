#include <iostream>
#include <stack>
#include <string>

using namespace std;

int main() {
    // ✅ stack 선언
    stack<int> s;            // 기본적으로 deque를 내부 컨테이너로 사용
    stack<string> st_str;    // 문자열 스택

    // ✅ 원소 삽입 (맨 위에 쌓임)
    s.push(10);
    s.push(20);
    s.push(30); // 현재 상태 (top부터): 30, 20, 10

    // ✅ 최상단 원소 확인 (삭제는 하지 않음)
    cout << "Top element: " << s.top() << endl; // 30

    // ✅ 최상단 원소 제거
    s.pop();  // 30 제거됨
    cout << "New top after pop: " << s.top() << endl; // 20

    // ✅ 비었는지 확인
    cout << (s.empty() ? "Stack is empty" : "Stack is not empty") << endl;

    // ✅ 크기 확인
    cout << "Stack size: " << s.size() << endl;

    // ✅ 문자열 예제
    st_str.push("Hello");
    st_str.push("World");
    while (!st_str.empty()) {
        cout << st_str.top() << " "; // LIFO 순 출력
        st_str.pop();
    }
    cout << endl;

    return 0;
}
