#include <iostream>
#include <set>

using namespace std;

int main() {
    // ✅ multiset 선언
    multiset<int> ms;

    // ✅ 값 삽입 (중복 허용)
    ms.insert(10);
    ms.insert(20);
    ms.insert(10); // 중복 허용
    ms.insert(30);
    ms.insert(10); // 또 삽입 가능

    // ✅ 자동 오름차순 정렬됨
    cout << "multiset contents: ";
    for (int x : ms) {
        cout << x << " "; // 10 10 10 20 30
    }
    cout << endl;

    // ✅ 특정 값의 개수 확인
    cout << "Number of 10s: " << ms.count(10) << endl;

    // ✅ 하나의 원소 삭제 (특정 하나만 삭제)
    auto it = ms.find(10); // 가장 앞에 있는 10
    if (it != ms.end()) ms.erase(it); // 한 개만 삭제됨

    cout << "After erasing one 10: ";
    for (int x : ms) cout << x << " "; // 10 10 20 30
    cout << endl;

    // ✅ 모든 10을 삭제
    ms.erase(10); // 동일한 값 전체 삭제

    cout << "After erasing all 10s: ";
    for (int x : ms) cout << x << " "; // 20 30
    cout << endl;

    // ✅ 정렬 기준 변경 (내림차순)
    multiset<int, greater<int>> ms2 = {1, 3, 2, 2, 1};
    cout << "Descending multiset: ";
    for (int x : ms2) cout << x << " "; // 3 2 2 1 1
    cout << endl;

    // ✅ 전체 삭제 및 확인
    ms2.clear();
    cout << "ms2 empty? " << (ms2.empty() ? "Yes" : "No") << endl;

    return 0;
}
