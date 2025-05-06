#include <iostream>
#include <vector>
#include <algorithm> // sort, reverse, find 등 포함

using namespace std;

int main() {
    // ✅ vector 선언 방법
    vector<int> v;                     // 빈 벡터 생성
    vector<int> v1 = {10, 20, 30};     // 초기화 리스트 사용
    vector<int> v2(5);                 // 크기 5, 모든 값은 0
    vector<int> v3(5, 1);              // 크기 5, 모든 값은 1

    // ✅ 값 할당
    v.assign(5, 2); // 기존 값 모두 삭제 후 2로 초기화된 5개의 원소 추가

    // ✅ 원소 접근 방법
    cout << "v[1]: " << v[1] << endl;       // 범위 검사 X, 속도 빠름
    cout << "v.at(1): " << v.at(1) << endl; // 범위 검사 O, 예외 발생 가능
    cout << "Front: " << v.front() << endl; // 첫 번째 원소
    cout << "Back: " << v.back() << endl;   // 마지막 원소

    // ✅ 삽입 및 삭제
    v.push_back(99);                        // 끝에 원소 추가
    v.pop_back();                           // 끝 원소 제거
    v.insert(v.begin() + 1, 100);           // 1번 인덱스에 100 삽입
    v.insert(v.begin() + 2, 3, 7);          // 2번 인덱스에 7을 3개 삽입
    v.erase(v.begin() + 1);                 // 1번 인덱스의 원소 삭제
    v.erase(v.begin() + 1, v.begin() + 4);  // 1~3번 인덱스 삭제
    v.clear();                              // 모든 원소 삭제 (capacity는 그대로)

    // ✅ 벡터 정보 출력
    cout << "Size: " << v.size() << endl;         // 현재 원소 개수
    cout << "Capacity: " << v.capacity() << endl; // 할당된 메모리 크기
    cout << "Is Empty: " << v.empty() << endl;    // 비었는지 확인

    // ✅ 벡터 간 값 교환
    v1.swap(v2); // 내용 및 capacity도 함께 교환됨

    // ✅ 정렬 및 탐색
    sort(v1.begin(), v1.end());              // 오름차순 정렬
    reverse(v1.begin(), v1.end());           // 내림차순 (reverse)
    auto it = find(v1.begin(), v1.end(), 20);
    if (it != v1.end())
        cout << "Found 20 at index: " << distance(v1.begin(), it) << endl;

    // ✅ 반복자 사용
    cout << "Iterator traversal: ";
    for (vector<int>::iterator it = v1.begin(); it != v1.end(); ++it)
        cout << *it << " ";
    cout << endl;

    // ✅ 범위 기반 for 문
    cout << "Range-based for loop: ";
    for (int val : v1)
        cout << val << " ";
    cout << endl;

    // ✅ C++11 이후: auto 키워드로 반복자 간단히 표현
    cout << "Using auto: ";
    for (auto it = v1.begin(); it != v1.end(); ++it)
        cout << *it << " ";
    cout << endl;

    // ✅ 메모리 최적화
    vector<int> v4;
    v4.reserve(100);   // capacity를 미리 확보 (재할당 방지)
    v4.shrink_to_fit(); // 사용 중인 메모리만 남기고 capacity 줄임

    return 0;
}