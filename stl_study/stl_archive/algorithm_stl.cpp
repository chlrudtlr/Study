#include <iostream>
#include <algorithm>
#include <vector>
#include <numeric> // accumulate
#include <functional> // greater

using namespace std;

int main() {
    vector<int> v = {5, 1, 3, 4, 2};

    // ✅ 정렬 (오름차순)
    sort(v.begin(), v.end()); // {1, 2, 3, 4, 5}

    // ✅ 정렬 (내림차순)
    sort(v.begin(), v.end(), greater<int>()); // {5, 4, 3, 2, 1}

    // ✅ 최대/최소
    cout << "max: " << *max_element(v.begin(), v.end()) << endl;
    cout << "min: " << *min_element(v.begin(), v.end()) << endl;

    // ✅ 합계
    int sum = accumulate(v.begin(), v.end(), 0);
    cout << "sum: " << sum << endl;

    // ✅ 조건 검색 (짝수 찾기)
    auto it = find_if(v.begin(), v.end(), [](int x) { return x % 2 == 0; });
    if (it != v.end()) cout << "짝수: " << *it << endl;

    // ✅ 전체 조건 검사
    cout << "모두 짝수? " << (all_of(v.begin(), v.end(), [](int x) { return x % 2 == 0; }) ? "Yes" : "No") << endl;
    cout << "하나라도 짝수? " << (any_of(v.begin(), v.end(), [](int x) { return x % 2 == 0; }) ? "Yes" : "No") << endl;

    // ✅ 특정 값 찾기
    if (find(v.begin(), v.end(), 3) != v.end())
        cout << "3 found\n";

    // ✅ reverse
    reverse(v.begin(), v.end()); // {1, 2, 3, 4, 5}

    // ✅ rotate
    rotate(v.begin(), v.begin() + 2, v.end()); // {3, 4, 5, 1, 2}

    // ✅ next_permutation
    vector<int> perm = {1, 2, 3};
    cout << "모든 순열:" << endl;
    do {
        for (int x : perm) cout << x << " ";
        cout << endl;
    } while (next_permutation(perm.begin(), perm.end()));

    // ✅ unique (중복 제거: 정렬 + unique + erase)
    vector<int> u = {1, 2, 2, 3, 3, 3, 4};
    sort(u.begin(), u.end()); // 먼저 정렬
    u.erase(unique(u.begin(), u.end()), u.end()); // 중복 제거
    cout << "중복 제거 후: ";
    for (int x : u) cout << x << " ";
    cout << endl;

    // ✅ lower_bound / upper_bound
    vector<int> a = {10, 20, 20, 30, 40};
    auto lb = lower_bound(a.begin(), a.end(), 20); // 첫 20 위치
    auto ub = upper_bound(a.begin(), a.end(), 20); // 20 초과 첫 위치
    cout << "20의 개수: " << (ub - lb) << endl;

    return 0;
}
