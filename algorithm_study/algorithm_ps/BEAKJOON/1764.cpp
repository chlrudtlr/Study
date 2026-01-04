#include <iostream>
#include <map>
#include <queue>

using namespace std;

int main() {
    cin.tie(NULL);
    ios::sync_with_stdio(false);

    map<string, bool> m;
    priority_queue<string, vector<string>, greater<string>> pq;
    int num_of_cannot_hear = 0;
    int num_of_cannot_see = 0;
    cin >> num_of_cannot_hear >> num_of_cannot_see;

    for (int i = 0; i < num_of_cannot_hear; i++) {
        string s;
        cin >> s;
        m[s] = true;
    }

    for (int i = 0; i < num_of_cannot_see; i++) {
        string s;
        cin >> s;
        if (m[s]) {
            pq.push(s);
        }
    }

    cout << pq.size() << endl;
    while (!pq.empty()) {
        cout << pq.top() << endl;
        pq.pop();
    }

    return 0;
}