// *** main.cpp ***
#ifndef _CRT_SECURE_NO_WARNINGS
#define _CRT_SECURE_NO_WARNINGS
#endif

#include <stdio.h>

#define CMD_INIT 100
#define CMD_UPDATE_SCORE 200
#define CMD_UNION_TEAM 300
#define CMD_GET_SCORE 400

extern void init(int N);
extern void updateScore(int mWinnerID, int mLoserID, int mScore);
extern void unionTeam(int mPlayerA, int mPlayerB);
extern int getScore(int mID);

static bool run()
{
    int queryCnt, cmd;
    int ans, res;
    bool okay = false;

    scanf("%d", &queryCnt);
    for (int i = 0; i < queryCnt; i++)
    {
        scanf("%d", &cmd);
        switch (cmd)
        {
        case CMD_INIT:
            int N;
            scanf("%d", &N);
            init(N);
            okay = true;
            break;
        case CMD_UPDATE_SCORE:
            int mWinnerID, mLoserID, mScore;
            scanf("%d%d%d", &mWinnerID, &mLoserID, &mScore);
            updateScore(mWinnerID, mLoserID, mScore);
            break;
        case CMD_UNION_TEAM:
            int mPlayerA, mPlayerB;
            scanf("%d%d", &mPlayerA, &mPlayerB);
            unionTeam(mPlayerA, mPlayerB);
            break;
        case CMD_GET_SCORE:
            int mID;
            scanf("%d", &mID);
            res = getScore(mID);
            scanf("%d", &ans);
            if (ans != res)
            {
                okay = false;
            }
            break;
        }
    }

    return okay;
}

/**
 * @brief Pro 시험 기출문제 - TC조별경기
 */

int main()
{
    setbuf(stdout, NULL);
    freopen("input.txt", "r", stdin);

    int T, MARK;
    scanf("%d%d", &T, &MARK);

    for (int tc = 1; tc <= T; tc++)
    {
        int score = run() ? MARK : 0;
        printf("#%d %d\n", tc, score);
    }

    return 0;
}

/**
 * N명의 선수들의 점수를 관리하는 프로그램을 작성 (4 ≤ N ≤ 100000)
 * 각 선수들은 서로 다른 ID를 가지며 ID는 1에서 N까지의 수 중 하나(ID가 a인 선수를 a번 선수)
 */

#include <iostream>
#include <vector>

using namespace std;

int num_of_players;
vector<int> score;        // 각 선수들의 점수
vector<int> parent;       // 각 선수들의 부모를 저장
vector<vector<int>> team; // root인 선수들에게 children 선수들 추가
vector<bool> isRoot;      // 해당 선수가 root인지 여부 -> team 벡터하고 같이 움직임

int FindParent(int id)
{
    if (parent[id] == id)
    {
        return id;
    }

    parent[id] = FindParent(parent[id]);
    return parent[id];
}

/**
 * N은 조별 경기에 참가한 선수들의 수 (4 ≤ N ≤ 100000)
 * 모든 선수들은 1인 1조로 출전
 * 최초 모든 선수들의 점수는 0점
 */
void init(int N)
{
    score.clear();
    parent.clear();
    team.clear();
    isRoot.clear();

    num_of_players = N;
    score.resize(num_of_players + 1, 0);      // 1-based
    parent.resize(num_of_players + 1, 0);     // 1-based
    team.resize(num_of_players + 1);          // 1-based
    isRoot.resize(num_of_players + 1, false); // 1-based

    for (int i = 0; i < num_of_players + 1; i++)
    {
        parent[i] = i;        // 처음에 자기 자신의 부모는 자기 자신
        team[i].push_back(i); // 각자의 부모가 자기 자신이므로
    }
}

/**
 * 서로 다른 두 조가 선정되어 경기를 진행하고 경기의 결과를 갱신하는 함수
 * ID가 mWinnerID인 선수가 속한 조가 승리, ID가 mLoserID인 선수가 속한 조가 패배 (1 ≤ mWinnerID, mLoserID ≤ N)
 * mScore만큼 승리한 조는 각자 점수를 얻고 패배란 조는 각자 점수를 잃는다 (1 ≤ mScore ≤ 100)
 */
void updateScore(int mWinnerID, int mLoserID, int mScore)
{
    int winner_parent = FindParent(mWinnerID);
    int loser_parent = FindParent(mLoserID);

    // 이긴 팀에 점수 추가
    for (int i = 0; i < team[winner_parent].size(); i++)
    {
        score[i] += mScore;
    }

    // 진 팀은 점수 제거
    for (int i = 0; i < team[loser_parent].size(); i++)
    {
        score[i] -= mScore;
    }
}

/**
 * 서로 다른 두 개의 조를 선정하여 하나의 조로 합치는 함수이다.
 * ID가 mPlayerA인 선수가 속한 조와 ID가 mPlayerB인 선수가 속한 조를 하나의 조로 합친다.
 */
void unionTeam(int mPlayerA, int mPlayerB)
{
    int parentA = FindParent(mPlayerA);
    int parentB = FindParent(mPlayerB);
}

/**
 * ID가 mID인 선수의 점수를 확인
 */
int getScore(int mID)
{
    return score[mID];
}