#include <iostream>
#include <list>

using namespace std;

int main() {
    // ✅ 리스트 선언
    list<int> lst;                // 빈 정수 리스트 생성
    list<int> lst2 = {1, 2, 3};   // 초기화 리스트 사용
    list<int> lst3(5, 100);       // 100으로 채워진 5개의 원소 생성

    // ✅ 원소 삽입
    lst.push_back(10);           // 뒤에 삽입
    lst.push_front(5);           // 앞에 삽입

    // ✅ 반복자 사용
    list<int>::iterator iter = lst.begin(); // 첫 원소를 가리키는 반복자

    // ✅ insert: 반복자가 가리키는 위치 앞에 삽입
    iter = lst.begin();
    lst.insert(iter, 7);         // 7을 첫 원소 앞에 삽입

    // ✅ erase: 특정 위치의 원소 삭제
    iter = lst.begin();
    lst.erase(iter);             // 첫 번째 원소 제거

    // ✅ 전체 출력 >> [] 연산자 없음 → lst[i]는 불가
    for (auto it = lst.begin(); it != lst.end(); ++it) {
        cout << *it << " ";
    }
    cout << endl;

    // ✅ 원소 제거
    lst.pop_back();              // 마지막 원소 제거
    lst.pop_front();             // 첫 번째 원소 제거
    lst.remove(100);             // 값이 100인 모든 원소 제거

    // ✅ 기타 함수
    cout << lst.size() << endl;      // 원소 수
    cout << (lst.empty() ? "empty" : "not empty") << endl; // 비었는지 여부
    cout << lst.front() << endl;     // 첫 원소
    cout << lst.back() << endl;      // 마지막 원소

    // ✅ 리스트 정렬 및 역순
    lst.sort();                  // 오름차순 정렬
    lst.reverse();               // 역순 정렬

    // ✅ 리스트 병합 (정렬된 상태여야 함) >> 정렬 후 병합 시 merge() 사용 가능 (정렬되지 않으면 이상하게 병합됨)
    lst2.sort();
    lst3.sort();
    lst2.merge(lst3);            // lst2에 lst3을 병합 (lst3은 비게 됨)

    // ✅ 리스트 교환
    lst.swap(lst2);              // 두 리스트의 내용 교환

    // ✅ 리스트 비우기
    lst.clear();                 // 모든 원소 삭제

    return 0;
}