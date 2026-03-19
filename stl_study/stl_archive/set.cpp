#include <iostream>
#include <set>

using namespace std;

int main() {
    // ✅ set 선언
    set<int> s; // 자동으로 오름차순 정렬, 중복 X

    // ✅ 값 삽입
    s.insert(30);
    s.insert(10);
    s.insert(20);
    s.insert(10); // 중복 삽입 무시됨

    // ✅ 출력 (오름차순으로 자동 정렬됨)
    cout << "Set contents: ";
    for (int x : s) {
        cout << x << " "; // 10 20 30
    }
    cout << endl;

    // ✅ 크기 확인
    cout << "Size: " << s.size() << endl; // 3

    // ✅ 값 존재 확인
    if (s.count(20)) {
        cout << "20 exists in set\n";
    }

    // ✅ 원소 삭제
    s.erase(20); // 값으로 삭제
    cout << "After erase(20): ";
    for (int x : s) cout << x << " "; // 10 30
    cout << endl;

    // ✅ 반복자 이용한 삭제
    auto it = s.find(10); // 10을 가리키는 반복자
    if (it != s.end()) {
        s.erase(it); // 반복자를 이용한 삭제
    }

    // ✅ 비어있는지 확인
    cout << (s.empty() ? "Set is empty" : "Set is not empty") << endl;

    // ✅ 전체 삭제
    s.clear();

    return 0;
}
