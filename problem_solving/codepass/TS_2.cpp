// main.cpp

#ifndef _CRT_SECURE_NO_WARNINGS
#define _CRT_SECURE_NO_WARNINGS
#endif

#include <stdio.h>

extern void init(int N, int K, int sCity[], int eCity[], int mLimit[]);
extern void add(int sCity, int eCity, int mLimit);
extern int calculate(int sCity, int eCity, int M, int mStopover[]);

/////////////////////////////////////////////////////////////////////////

#define MAX_E 2000
#define MAX_S 3
#define CMD_INIT 100
#define CMD_ADD 200
#define CMD_CALC 300

static bool run()
{
    int q;
    scanf("%d", &q);

    int n, m, k;
    char strTmp[20];
    int sCityArr[MAX_E], eCityArr[MAX_E], mLimitArr[MAX_E], mStopover[MAX_S];
    int sCity, eCity, mLimit;
    int cmd, ans, ret = 0;
    bool okay = false;

    for (int i = 0; i < q; ++i)
    {
        scanf("%d %s", &cmd, strTmp);
        switch (cmd)
        {
        case CMD_INIT:
            okay = true;
            scanf("%s %d %s %d", strTmp, &n, strTmp, &k);
            for (int j = 0; j < k; ++j)
            {
                scanf("%s %d %s %d %s %d", strTmp, &sCityArr[j], strTmp, &eCityArr[j], strTmp, &mLimitArr[j]);
            }
            init(n, k, sCityArr, eCityArr, mLimitArr);
            break;
        case CMD_ADD:
            scanf("%s %d %s %d %s %d", strTmp, &sCity, strTmp, &eCity, strTmp, &mLimit);
            add(sCity, eCity, mLimit);
            break;
        case CMD_CALC:
            scanf("%s %d %s %d %s %d", strTmp, &sCity, strTmp, &eCity, strTmp, &m);
            for (int j = 0; j < m; ++j)
            {
                scanf("%s %d", strTmp, &mStopover[j]);
            }
            scanf("%s %d", strTmp, &ans);
            ret = calculate(sCity, eCity, m, mStopover);
            if (ans != ret)
                okay = false;
            break;
        default:
            okay = false;
            break;
        }
    }
    return okay;
}

int main()
{
    setbuf(stdout, NULL);
    freopen("input2.txt", "r", stdin);

    int T, MARK;
    scanf("%d %d", &T, &MARK);

    for (int tc = 1; tc <= T; tc++)
    {
        int score = run() ? MARK : 0;
        printf("#%d %d\n", tc, score);
    }

    return 0;
}

/**
 * @brief Pro 시험 기출문제 - TC경유지운송
 * @details
 * N개의 도시가 주어진다. 각 도시는 0부터 N-1까지 ID값을 가진다.
 * 도시를 연결하는 양방향 도로가 추가될 때, 해당 도로를 이용할 수 있는 최대 중량이 주어진다.
 * 출발 도시와 도착 도시, 그리고 경유지가 주어졌을 때, 운송할 수 있는 화물의 최대 중량을 구하고자 한다.
 * 경유지는 최대 3개 주어지며, 순서에 상관 없이 방문하면 된다. 동일한 경유지를 여러 번 방문할 수 있고,
 * 경유지를 방문하기 위해 출발 도시나 도착 도시를 거쳐서 가도 된다.
 */

#include <iostream>
#include <queue>
#include <vector>
#include <map>
#include <algorithm>

using namespace std;

int num_of_city;
int num_of_road;
vector<vector<int>> city;           // 도시 연결 정보 저장
map<pair<int, int>, int> roadLimit; // 도로 연결 정보 저장
vector<bool> visited;               // 방문 여부 저장
vector<int> maxLimit;               // 각 도시까지 운송 가능한 최대 크기 저장

bool debug = false;

/**
 * N개의 도시와 K개의 양방향 도로 정보가 주어진다.
 * N: 도시의 개수 ( 5 ≤ N ≤ 1,000 )
 * K: 도로의 개수 ( 2 ≤ K ≤ 2,000 )
 * 각 테스트 케이스의 처음에 호출된다.
 * sCity[i]: 도로 i와 연결된 도시 ( 0 ≤ sCity[i] < N )
 * eCity[i]: 도로 i와 연결된 도시 ( 0 ≤ eCity[i] < N )
 * mLimit[i]: 도로 i를 이용할 수 있는 최대 중량 ( 1 ≤ mLimit[i] ≤ 30,000 )
 */
void init(int N, int K, int sCity[], int eCity[], int mLimit[])
{
    debug = false;

    // ==================== Clear ====================
    num_of_city = 0;
    num_of_road = 0;
    city.clear();
    roadLimit.clear();
    visited.clear();
    maxLimit.clear();

    // ==================== Initalize ====================
    num_of_city = N;
    num_of_road = K;
    city.resize(num_of_city + 1);
    visited.resize(num_of_city + 1, false);
    maxLimit.resize(num_of_city + 1, 0);
    for (int i = 0; i < num_of_road; i++)
    {
        city[sCity[i]].push_back(eCity[i]);
        city[eCity[i]].push_back(sCity[i]);
        roadLimit[make_pair(sCity[i], eCity[i])] = mLimit[i];
        roadLimit[make_pair(eCity[i], sCity[i])] = mLimit[i];
    }

    if (debug)
    {
        cout << "==================== Initalize ====================" << endl;
        cout << "num_of_city : " << num_of_city << endl;
        cout << "num_of_road : " << num_of_road << endl;
        for (int i = 0; i < num_of_road; i++)
        {
            cout << sCity[i] << " and " << eCity[i] << " is connected : " << mLimit[i] << endl;
        }
    }

    return;
}

/**
 * sCity 도시와 eCity 도시를 연결하는 양방향 도로를 추가
 * 도로를 이용할 수 있는 최대 중량은 mLimit ( 1 ≤ mLimit ≤ 30,000 )
 */
void add(int sCity, int eCity, int mLimit)
{
    city[sCity].push_back(eCity);
    city[eCity].push_back(sCity);
    roadLimit[make_pair(sCity, eCity)] = mLimit;
    roadLimit[make_pair(eCity, sCity)] = mLimit;
    num_of_road++;

    if (debug)
    {
        cout << "==================== ADD ====================" << endl;
        cout << "Add " << sCity << " <-> " << eCity << " : " << mLimit << endl;
        cout << "num_of_road : " << num_of_road << endl;
    }

    return;
}

/**
 * M개의 경유지가 mStopover 배열로 주어진다.
 * M: 경유지 개수 ( 1 ≤ M ≤ 3)
 * sCity에서 M개의 경유지를 거쳐서 eCity까지 운송할 수 있는 화물의 최대 중량을 반환한다.
 * 운송이 불가능하다면, -1을 반환한다.
 */
int calculate(int sCity, int eCity, int M, int mStopover[])
{
    visited.clear();
    maxLimit.clear();
    visited.resize(num_of_city + 1, false);
    maxLimit.resize(num_of_city + 1, 0);

    // sCity에서 eCity까지 다익스트라
    priority_queue<pair<int, int>> pq;
    pq.push(make_pair(987654321, sCity));
    maxLimit[sCity] = 987654321; // pq에 넣는 것 뿐만 아니라 초기화도 해야됨
    while (!pq.empty())
    {
        int cur_city = pq.top().second;
        int cur_limit = pq.top().first;

        pq.pop();

        if (cur_limit < maxLimit[cur_city])
        {
            continue;
        }

        for (int i = 0; i < city[cur_city].size(); i++)
        {
            int tmp_limit = min(cur_limit, roadLimit[make_pair(cur_city, city[cur_city][i])]);
            if (tmp_limit > maxLimit[city[cur_city][i]])
            {
                maxLimit[city[cur_city][i]] = tmp_limit;
                pq.push(make_pair(tmp_limit, city[cur_city][i]));
            }
        }
    }

    int result = 987654321;
    result = min(result, maxLimit[eCity]);
    for (int i = 0; i < M; i++)
    {
        if (maxLimit[mStopover[i]] == 0)
        {
            result = -1;
            break;
        }
        result = min(result, maxLimit[mStopover[i]]);
    }

    if (maxLimit[eCity] == 0)
    {
        result = -1;
    }

    if (debug)
    {
        cout << "==================== Calculate ====================" << endl;
        cout << "Start : " << sCity << " / End : " << eCity << endl;
        cout << "Stopped : ";
        for (int i = 0; i < M; i++)
        {
            cout << mStopover[i] << " ";
        }
        cout << endl;
        cout << "result : " << result << endl;
    }
    return result;
}