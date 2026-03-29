/**
 * @file 백준 1753번
 * @category Dijkstra
 *
 * @details
 * 그냥 전형적인 다익스트라 문제
 */
#include <iostream>
#include <vector>

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

    // 간선 정보에 대한 input 받기
    for (int i = 0; i < E; i++)
    {
        int u = 0, v = 0, w = 0; // u에서 v로 가는 가중치 w인 간선이 존재한다는 뜻
        cin >> u >> v >> w;
        field[u].push_back(make_pair(v, w));
    }

    return 0;
}