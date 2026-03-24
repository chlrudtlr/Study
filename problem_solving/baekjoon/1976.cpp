/**
 * @file 백준 1976번
 * @category union-find
 *
 * @details
 * 도시들끼리 Union find를 수행한 후에
 * 도시들의 parent가 동일하면 여행가능한 도시라고 판단
 */
#include <iostream>
#include <vector>

using namespace std;

int N; // 전체 도시의 수 < 200
int M; // 여행할 도시의 수 < 1000
vector<int> Parent;
vector<int> Rank;

int FindParent(int node)
{
    if (Parent[node] == node)
    {
        return node;
    }

    Parent[node] = FindParent(Parent[node]);
    return Parent[node];
}

void Union(int a, int b)
{
    int parentA = FindParent(a);
    int parentB = FindParent(b);

    if (parentA == parentB)
    {
        return;
    }

    if (Rank[parentA] < Rank[parentB])
    {
        Parent[parentA] = parentB;
    }
    else if (Rank[parentA] > Rank[parentB])
    {
        Parent[parentB] = parentA;
    }
    else
    {
        Parent[parentB] = parentA;
        Rank[parentA]++;
    }
}

int main()
{
    cin >> N >> M;

    Parent.resize(N, 0);
    Rank.resize(N, 0);

    // Init
    for (int i = 0; i < Parent.size(); i++)
    {
        Parent[i] = i;
    }

    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
        {
            int is_connected = 0;
            cin >> is_connected;
            if (is_connected == 1)
            {
                Union(i, j);
            }
        }
    }

    int cur_root = 0;
    int prev_root = 0;
    for (int i = 0; i < M; i++)
    {
        int city = 0;
        cin >> city;
        cur_root = Parent[city - 1]; // 0-based

        if ((i != 0) && (prev_root != cur_root))
        {
            cout << "NO" << endl;
            return 0;
        }
        else
        {
            prev_root = cur_root;
        }
    }

    cout << "YES" << endl;
    return 0;
}