#include <iostream>
#include <queue>
#include <vector>

using namespace std;

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(NULL);
    std::cout.tie(NULL);

    priority_queue<int, vector<int>, greater<int>> pq;

    int N = 0;
    cin >> N;
    for (int i = 0; i < N; i++) {
        int a = 0;
        cin >> a;
        if (a > 0) {
            pq.push(a);
        } else if (a == 0) {
            if (pq.empty()) {
                cout << "0" << '\n';
            } else {
                cout << pq.top() << '\n';
                pq.pop();
            }
        }
    }

    return 0;
}