#include <iostream>
#include <queue>
#include <string>

using namespace std;

int main() {
    // ✅ queue 선언
    queue<int> q;             // 정수 큐
    queue<string> qs;         // 문자열 큐

    // ✅ 값 삽입 (back에 들어감)
    q.push(10);
    q.push(20);
    q.push(30); // 현재 상태: front → 10, 20, 30 ← back

    // ✅ front, back 확인
    cout << "Front: " << q.front() << endl; // 10
    cout << "Back: " << q.back() << endl;   // 30

    // ✅ pop (front 제거)
    q.pop(); // 10 제거
    cout << "New front: " << q.front() << endl; // 20

    // ✅ 비었는지 확인
    cout << (q.empty() ? "Queue is empty" : "Queue is not empty") << endl;

    // ✅ 원소 개수
    cout << "Queue size: " << q.size() << endl;

    // ✅ 문자열 queue 예제
    qs.push("first");
    qs.push("second");
    qs.push("third");
    cout << "String queue: ";
    while (!qs.empty()) {
        cout << qs.front() << " ";
        qs.pop();
    }
    cout << endl;

    return 0;
}