/**
 * @file 백준 1043번
 * @category union-find
 *
 * @details
 * 같은 파티에 있던 친구들끼리 Union Find
 * 진실을 알고 있는 친구와 부모 Node가 같은 애들은 전부 진실쟁이
 */
#include <iostream>
#include <vector>
#include <map>

using namespace std;

int N;        // 사람 수
int M;        // 파티 수
int truthNum; // 진실을 아는 사람의 수
vector<int> truthFriends;
vector<vector<int>> friendsInParty;

vector<int> parentFriends;
vector<int> rankFriends;

int FindParent(int a)
{
    if (parentFriends[a] == a)
    {
        return a;
    }

    parentFriends[a] = FindParent(a);
    return parentFriends[a];
}

void Union(int a, int b)
{
    int parentA = FindParent(a);
    int parentB = FindParent(b);

    if (parentA == parentB)
    {
        return;
    }

    if (rankFriends[parentA] < rankFriends[parentB])
    {
        parentFriends[parentA] = parentB;
    }
    else if (rankFriends[parentA] > rankFriends[parentB])
    {
        parentFriends[parentB] = parentA;
    }
    else
    {
        parentFriends[parentB] = parentA;
        rankFriends[parentA]++;
    }
}

int main()
{
    cin >> N >> M;
    cin >> truthNum;
    for (int i = 0; i < truthNum; i++)
    {
        int f = 0;
        cin >> f;
        truthFriends.push_back(f);
    }

    // Init
    friendsInParty.resize(M + 2);
    parentFriends.resize(N, 0);
    rankFriends.resize(N, 0);
    for (int i = 0; i < N; i++)
    {
        parentFriends[i] = i;
    }

    // 각 파티에 참석한 사람의 명단을 받으면서 Union
    for (int i = 0; i < M; i++)
    {
        int count = 0; // i번째 파티에 온 친구 수
        cin >> count;

        for (int j = 0; j < count; j++)
        {
            int n = 0;
            cin >> n;
            friendsInParty[i].push_back(n);
        }

        for (int j = 0; j < count - 1; j++)
        {
            Union(friendsInParty[i][j], friendsInParty[i][j + 1]);
        }
    }

    // Prepare
    map<int, bool> m;
    for (int i = 0; i < truthFriends.size(); i++)
    {
        m[FindParent(truthFriends[i])] = true;
    }

    // 이제 각 파티를 돌면서 진실쟁이가 없는 파티를 찾으면 된다. 아마도
    for (int i = 0; i < M; i++)
    {
    }
}