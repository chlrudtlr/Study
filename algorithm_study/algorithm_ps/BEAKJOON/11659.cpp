#include <iostream>
#include <vector>

using namespace std;

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(NULL);
    std::cout.tie(NULL);

    // 수의 개수 N과 합을 구해야 하는 횟수 M
    int n = 0, m = 0;
    vector<int> v;

    cin >> n >> m;

    for (int i = 0; i < n; i++) {
        int a = 0;
        cin >> a;
        if (i == 0) {
            v.push_back(a);
        } else {
            v.push_back(a + v[i - 1]);
        }
    }

    for (int i = 0; i < m; i++) {
        int start = 0, end = 0;
        cin >> start >> end;
        cout << v[end - 1] - v[start - 2] << '\n';
    }

    return 0;
}