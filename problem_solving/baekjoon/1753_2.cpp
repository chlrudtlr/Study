/**
 * @file 백준 1753번-GPT가 개선해준 코드
 * @category Dijkstra
 *
 * @details
 * 시작 정점 K에서 모든 정점까지의 최단거리를 구하는 전형적인 다익스트라 문제
 */
#include <iostream>
#include <vector>
#include <queue>

using namespace std;

const int INF = 987654321;

int V; // 정점의 개수
int E; // 간선의 개수
int K; // 시작 정점

// graph[u] = { {cost, v}, {cost, v}, ... }
vector<vector<pair<int, int>>> graph;
vector<int> dist;

int main()
{
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> V >> E;
    cin >> K;

    graph.resize(V + 1);
    dist.resize(V + 1, INF);

    for (int i = 0; i < E; i++)
    {
        int u = 0;
        int v = 0;
        int w = 0;
        cin >> u >> v >> w;

        graph[u].push_back({w, v});
    }

    priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> pq;

    dist[K] = 0;
    pq.push({0, K});

    while (!pq.empty())
    {
        int cur_dist = pq.top().first;
        int cur_pos = pq.top().second;
        pq.pop();

        // pq 안에 들어 있던 오래된 정보면 무시
        if (cur_dist > dist[cur_pos])
        {
            continue;
        }

        for (int i = 0; i < (int)graph[cur_pos].size(); i++)
        {
            int next_dist = graph[cur_pos][i].first;
            int next_pos = graph[cur_pos][i].second;

            if (cur_dist + next_dist < dist[next_pos])
            {
                dist[next_pos] = cur_dist + next_dist;
                pq.push({dist[next_pos], next_pos});
            }
        }
    }

    for (int i = 1; i <= V; i++)
    {
        if (dist[i] == INF)
        {
            cout << "INF\n";
        }
        else
        {
            cout << dist[i] << '\n';
        }
    }

    return 0;
}