#include <iostream>
#include <map>
#include <string>

using namespace std;

int main() {
    // ✅ map 선언과 초기화
    map<string, int> m;  // key: string, value: int

    // ✅ 값 삽입 방법
    m["apple"] = 3;             // 방법 1: 대괄호 연산자 사용 (존재하지 않으면 새로 생성됨)
    m.insert({"banana", 5});    // 방법 2: insert()로 pair 삽입
    m.insert(make_pair("cherry", 2)); // 방법 3: make_pair 사용

    // ✅ 중복 key는 허용되지 않음 → 기존 값 덮어쓰기
    m["apple"] = 10; // 기존 "apple" 값을 10으로 수정

    // ✅ map 출력 (key 기준 오름차순 자동 정렬)
    cout << "map contents:" << endl;
    for (auto it = m.begin(); it != m.end(); ++it) {
        cout << it->first << " : " << it->second << endl;
    }

    // ✅ 특정 key 존재 여부 확인
    if (m.count("banana")) {
        cout << "banana exists" << endl;
    }

    // ✅ 값 접근
    cout << "apple's value: " << m["apple"] << endl;
    // 주의: 없는 key 접근 시 새로 생성됨 → 값을 변경하지 않아도 메모리에 추가됨

    // ✅ at() 접근: 존재하지 않는 key 접근 시 예외 발생
    try {
        cout << "cherry: " << m.at("cherry") << endl;
        // cout << "pear: " << m.at("pear") << endl; // 예외 발생 (존재하지 않음)
    } catch (const out_of_range& e) {
        cout << "Exception: " << e.what() << endl;
    }

    // ✅ 원소 삭제
    m.erase("banana");             // key로 삭제
    m.erase(m.find("cherry"));     // 반복자로 삭제

    // ✅ 전체 삭제
    m.clear();

    // ✅ 상태 확인
    cout << "Size: " << m.size() << endl;
    cout << "Empty: " << (m.empty() ? "Yes" : "No") << endl;

    // ✅ 커스텀 정렬 기준 (내림차순 key 정렬)
    map<int, string, greater<int>> m2;
    m2[1] = "one";
    m2[5] = "five";
    m2[3] = "three";

    cout << "\nDescending map:" << endl;
    for (auto& p : m2) {
        cout << p.first << " : " << p.second << endl;
    }

    return 0;
}
