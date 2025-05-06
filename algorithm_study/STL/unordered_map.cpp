#include <iostream>
#include <unordered_map>
#include <string>

using namespace std;

int main() {
    // ✅ unordered_map 선언
    unordered_map<string, int> um;

    // ✅ 값 삽입
    um["apple"] = 3;                      // 방법 1: 대괄호
    um.insert({"banana", 5});            // 방법 2: insert(pair)
    um.insert(make_pair("cherry", 2));   // 방법 3: make_pair

    // ✅ 중복 key는 무시됨 → 기존 값 덮어씀
    um["apple"] = 10;

    // ✅ 출력 (정렬 X, 해시 기반 → 순서 보장 안됨)
    cout << "unordered_map contents:" << endl;
    for (auto it = um.begin(); it != um.end(); ++it) {
        cout << it->first << " : " << it->second << endl;
    }

    // ✅ 특정 key 존재 확인
    if (um.count("banana")) {
        cout << "banana exists" << endl;
    }

    // ✅ 값 접근
    cout << "apple's value: " << um["apple"] << endl;

    // ✅ at() 접근 (존재하지 않으면 예외 발생)
    try {
        cout << "cherry: " << um.at("cherry") << endl;
        // cout << "pear: " << um.at("pear") << endl; // 예외 발생
    } catch (const out_of_range& e) {
        cout << "Exception: " << e.what() << endl;
    }

    // ✅ 원소 삭제
    um.erase("banana");                   // key로 삭제
    um.erase(um.find("cherry"));         // 반복자로 삭제

    // ✅ 전체 삭제
    um.clear();

    // ✅ 상태 확인
    cout << "Size: " << um.size() << endl;
    cout << "Empty: " << (um.empty() ? "Yes" : "No") << endl;

    return 0;
}
