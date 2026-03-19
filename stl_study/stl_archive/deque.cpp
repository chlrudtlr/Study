#include <iostream>
#include <deque>

using namespace std;

int main() {
    // ✅ deque 선언과 초기화
    deque<int> d;                    // 빈 deque
    deque<int> d1(5);                // 0으로 초기화된 5개의 원소
    deque<int> d2(5, 10);            // 10으로 초기화된 5개의 원소
    deque<int> d3 = {1, 2, 3, 4};    // 리스트 초기화
    deque<int> d4(d3);               // 다른 deque로 복사

    // ✅ 원소 삽입 / 삭제
    d.push_back(100);               // 뒤에 삽입
    d.push_front(200);              // 앞에 삽입
    d.pop_back();                   // 뒤에서 제거 (값 반환 X)
    d.pop_front();                  // 앞에서 제거

    // ✅ 임의 위치 삽입 / 삭제
    d.insert(d.begin() + 2, 999);   // 2번째 위치에 999 삽입
    d.erase(d.begin() + 2);         // 2번째 원소 제거

    // ✅ 원소 접근
    cout << d[2] << endl;           // 인덱스로 접근 (범위 체크 X)
    cout << d.at(2) << endl;        // 범위 체크 포함
    cout << d.front() << endl;      // 첫 원소
    cout << d.back() << endl;       // 마지막 원소

    // ✅ 정보 확인
    cout << d.size() << endl;       // 원소 수
    cout << d.empty() << endl;      // 비어있는지 여부

    // ✅ 반복자
    for (deque<int>::iterator it = d.begin(); it != d.end(); ++it) {
        cout << *it << " ";
    }
    cout << endl;

    // ✅ 기타
    d.clear();                      // 모든 원소 삭제
    d.shrink_to_fit();              // 여유 capacity 줄이기 (C++11~)

    return 0;
}
