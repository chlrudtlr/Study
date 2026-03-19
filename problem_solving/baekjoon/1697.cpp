// 1697. 숨박꼭질
// https://www.acmicpc.net/problem/1697
#include <iostream>
#include <queue>

using namespace std;

int main()
{
    queue<int> q;
    vector<bool> visited(100005, false);
    // N(0 ≤ N ≤ 100000)
    // K(0 ≤ K ≤ 100000)
    int N = 0, K = 0;
    cin >> N >> K;

    q.push(N);
    visited[N] = true;

    int time = 0; // 찾는데 걸린 시간
    while (!q.empty())
    {
        int qs = q.size();
        for (int i = 0; i < qs; i++)
        {
            int pos = q.front();
            q.pop();

            if (pos == K)
            {
                cout << time << endl;
                return 0;
            }

            if (pos - 1 <= 100000 && pos - 1 >= 0 && !visited[pos - 1])
            {
                q.push(pos - 1);
                visited[pos - 1] = true;
            }
            if (pos + 1 <= 100000 && pos + 1 >= 0 && !visited[pos + 1])
            {
                q.push(pos + 1);
                visited[pos + 1] = true;
            }
            if (pos * 2 <= 100000 && pos * 2 >= 0 && !visited[pos * 2])
            {
                q.push(pos * 2);
                visited[pos * 2] = true;
            }
        }
        time++;
    }

    cout << time << endl;
    return 0;
}