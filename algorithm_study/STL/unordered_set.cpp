#include <iostream>
#include <unordered_set>

using namespace std;

int main() {
    // ✅ unordered_set 선언
    unordered_set<int> us;

    // ✅ 값 삽입 (순서는 보장되지 않음)
    us.insert(30);
    us.insert(10);
    us.insert(20);
    us.insert(10); // 중복 무시

    // ✅ 출력 (삽입 순서 아님, 정렬되지 않음)
    cout << "unordered_set contents: ";
    for (int x : us) {
        cout << x << " ";
    }
    cout << endl;

    // ✅ 값 존재 확인
    if (us.count(20)) {
        cout << "20 exists in unordered_set\n";
    }

    // ✅ 값 삭제
    us.erase(20); // 값으로 삭제
    cout << "After erase(20): ";
    for (int x : us) cout << x << " ";
    cout << endl;

    // ✅ 반복자 사용한 삭제
    auto it = us.find(10);
    if (it != us.end()) {
        us.erase(it); // 반복자 삭제
    }

    // ✅ 전체 삭제
    us.clear();

    // ✅ 상태 확인
    cout << "Size: " << us.size() << endl;
    cout << (us.empty() ? "Set is empty" : "Set is not empty") << endl;

    return 0;
}
