/**
 * @file 백준 1753번
 * @category Dijkstra
 *
 * @details
 * 그냥 전형적인 다익스트라 문제
 */
#include <iostream>
#include <vector>
#include <queue>

using namespace std;

int V; // 정점의 갯수(1 ≤ V ≤ 20000), 1-based
int E; // 간선의 갯수(1 ≤ E ≤ 300000), 1-based

vector<vector<pair<int, int>>> field; // 연결 벡터
vector<bool> visited;                 // 도착(결정) 여부
vector<int> dist;                     // 시작 지점부터 해당 지점까지의 거리
int K;                                // 시작 노드(1 ≤ K ≤ V)

int main()
{
    cin >> V >> E;
    cin >> K;

    // Init - 약간 여유있게 잡았으니까 .size()로 접근하지 말고 V, E 사용하기
    field.resize(V + 5);
    visited.resize(V + 5, false);
    dist.resize(V + 5, 987654321);
    dist[K] = 0; // 시작점이라서 0으로 세팅해주긴 하는데 여기서 해주는게 맞나
    visited[K] = true;

    // 간선 정보에 대한 input 받기
    for (int i = 0; i < E; i++)
    {
        int u = 0, v = 0, w = 0; // u에서 v로 가는 가중치 w인 간선이 존재한다는 뜻
        cin >> u >> v >> w;
        field[u].push_back(make_pair(v, w));
    }

    // 다익스트라 알고리즘
    /**
     * 수정할 부분
     * pq는 거리 작은 순으로 정렬되도록 하기
     * 거리 갱신될 때만 pq에 넣기
     * visited 사용하기
     */
    priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> pq;
    pq.push(make_pair(dist[K], K));
    while (!pq.empty())
    {
        int cur_pos = pq.top().second;
        int cur_dist = pq.top().first;
        pq.pop();

        for (int i = 0; i < field[cur_pos].size(); i++)
        {
            int next_pos = field[cur_pos][i].second;
            int next_dist = field[cur_pos][i].first;
            if (cur_dist + next_dist < dist[next_pos])
            {
                dist[next_pos] = cur_dist + next_dist;
                visited[next_pos] = true;
            }
            pq.push(make_pair(dist[next_pos], next_pos));
        }
    }

    // 결과 출력
    for (int i = 1; i < V + 1; i++) // 1-based
    {
        if (dist[i] == 987654321)
        {
            cout << "INF" << endl;
        }
        else
        {
            cout << dist[i] << endl;
        }
    }

    return 0;
}