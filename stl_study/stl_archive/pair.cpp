#include <iostream>
#include <utility>   // for std::pair
#include <vector>
#include <algorithm> // for sort
#include <queue>     // for priority_queue

using namespace std;

int main() {
    // ✅ pair 선언과 초기화
    pair<int, string> p1 = {1, "apple"};
    pair<int, string> p2(2, "banana");
    auto p3 = make_pair(3, "cherry");

    cout << "p1: (" << p1.first << ", " << p1.second << ")\n";
    cout << "p2: (" << p2.first << ", " << p2.second << ")\n";
    cout << "p3: (" << p3.first << ", " << p3.second << ")\n";

    // ✅ 비교 연산자 사용 가능 (first → second 순으로 자동 비교)
    cout << (p1 < p2 ? "p1 < p2" : "p1 >= p2") << endl;

    // ✅ vector<pair> 사용 예시
    vector<pair<int, string>> vec = {
        {2, "banana"},
        {3, "cherry"},
        {1, "apple"}
    };

    // 정렬: first 기준 오름차순
    sort(vec.begin(), vec.end());

    cout << "✅ sorted pair vector:\n";
    for (auto& p : vec)
        cout << "(" << p.first << ", " << p.second << ")\n";

    // ✅ pair를 이용한 좌표 표현
    pair<int, int> pos = {3, 4};
    cout << "position: x=" << pos.first << ", y=" << pos.second << endl;

    // ✅ pair를 사용하는 priority_queue (min-heap by first)
    priority_queue<pair<int, string>, vector<pair<int, string>>, greater<>> pq;
    pq.push({3, "low"});
    pq.push({1, "high"});
    pq.push({2, "medium"});

    cout << "✅ priority_queue<pair> (by first asc):\n";
    while (!pq.empty()) {
        auto p = pq.top(); pq.pop();
        cout << p.first << " → " << p.second << endl;
    }

    // ✅ pair 활용: swap
    pair<int, int> a = {1, 100}, b = {2, 200};
    swap(a, b);
    cout << "after swap: a=(" << a.first << ", " << a.second << ")\n";

    // ✅ tie()를 이용한 pair 분해
    pair<int, string> p = {10, "example"};
    int num;
    string word;
    tie(num, word) = p;
    cout << "tie unpacked: num=" << num << ", word=" << word << endl;

    // ✅ 구조적 바인딩 (C++17 이상)
#if __cplusplus >= 201703L
    auto [id, name] = p;
    cout << "structured binding: id=" << id << ", name=" << name << endl;
#endif

    return 0;
}
