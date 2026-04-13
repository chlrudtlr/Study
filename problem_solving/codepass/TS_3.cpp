// main.cpp

#ifndef _CRT_SECURE_NO_WARNINGS
#define _CRT_SECURE_NO_WARNINGS
#endif

#include <stdio.h>

#define MAX_N (100)
#define MAX_M (5000)

struct RESULT
{
    int heights[MAX_N][MAX_N];
};

static RESULT user_ans;
static int m_ice_block[MAX_N][MAX_N];
static int ice_group[MAX_M][3];

extern void init(int N, int M, int iceBlock[MAX_N][MAX_N], int mIceGroup[MAX_M][3]);
extern RESULT oneYearLater(void);

static int run(void)
{
    int n, m, k;
    scanf("%d%d%d", &n, &m, &k);

    for (int y = 0; y < n; y++)
    {
        for (int x = 0; x < n; x++)
        {
            scanf("%d", &m_ice_block[y][x]);
        }
    }

    for (int i = 0; i < m; i++)
    {
        scanf("%d%d%d", &ice_group[i][0], &ice_group[i][1], &ice_group[i][2]);
    }

    init(n, m, m_ice_block, ice_group);

    bool ret = true;

    for (int query = 0; query < k; query++)
    {
        user_ans = oneYearLater();
        for (int y = 0; y < n; y++)
        {
            for (int x = 0; x < n; x++)
            {
                int correct_ans;
                scanf("%d", &correct_ans);
                if (user_ans.heights[y][x] != correct_ans)
                    ret = false;
            }
        }
    }

    return ret;
}

int main()
{
    freopen("input3.txt", "r", stdin);
    int tc, score;
    scanf("%d%d", &tc, &score);

    for (int t = 1; t <= tc; t++)
    {
        if (run())
            printf("#%d %d\n", t, score);
        else
            printf("#%d %d\n", t, 0);
    }

    return 0;
}

/**
 * @brief Pro 시험 기출문제 - TC빙하의 이동
 * @details
 * N x N 크기의 바다가 있다.
 * a. 융해 : 상하좌우 바다에 인접한 얼음덩어리의 높이가 1 씩 줄어든다.
 * b. 이동 : 빙하가 상하좌우 중 한 방향으로 1 칸씩 이동한다.
 * c. 병합 : 다른 빙하가 서로 충돌하거나, 상하좌우로 인접할 경우 하나의 빙하가 된다.
 */

// 위에 선언되어 있어서 일단 주석처리 했음
// struct RESULT
// {
//     int heights[MAX_N][MAX_N];
// };
#include <iostream>
#include <iomanip>
#include <vector>
#include <map>

#define MAX_N (100)
#define MAX_M (5000)

using namespace std;

int field_size;
int num_of_ice;
int year;
vector<vector<int>> field;
vector<vector<int>> field_ID;
map<int, int> dir_of_ice;
map<int, int> vol_of_ice;

bool debug;

void printfield()
{
    cout << "<<<<<<<<<<<<<<<<<<<< Ice Field >>>>>>>>>>>>>>>>>>>>" << endl;
    for (int i = 0; i < field_size; i++)
    {
        for (int j = 0; j < field_size; j++)
        {
            cout << setw(4) << field[i][j] << " ";
        }
        cout << endl;
    }
}

void printfieldId()
{
    cout << "<<<<<<<<<<<<<<<<<<<< Ice Field ID >>>>>>>>>>>>>>>>>>>>" << endl;
    for (int i = 0; i < field_size; i++)
    {
        for (int j = 0; j < field_size; j++)
        {
            cout << setw(4) << field_ID[i][j] << " ";
        }
        cout << endl;
    }
}

void Marking(int x, int y, int count)
{
    field_ID[x][y] = count;
    vol_of_ice[count] += field[x][y]; // marking 할 때 마다 해당 아이디에 해당하는 빙하의 부피에 더해주기
    // 상
    if ((x - 1 >= 0) && (field[x - 1][y] != 0) && (field_ID[x - 1][y] == 0))
    {
        Marking(x - 1, y, count);
    }
    else if ((x == 0) && (field[field_size - 1][y] != 0) && (field_ID[field_size - 1][y] == 0))
    {
        Marking(field_size - 1, y, count);
    }
    // 하
    if ((x + 1 < field_size) && (field[x + 1][y] != 0) && (field_ID[x + 1][y] == 0))
    {
        Marking(x + 1, y, count);
    }
    else if ((x == field_size - 1) && (field[0][y] != 0) && (field_ID[0][y] == 0))
    {
        Marking(0, y, count);
    }
    // 좌
    if ((y - 1 >= 0) && (field[x][y - 1] != 0) && (field_ID[x][y - 1] == 0))
    {
        Marking(x, y - 1, count);
    }
    else if ((y == 0) && (field[x][field_size - 1] != 0) && (field_ID[x][field_size - 1] == 0))
    {
        Marking(x, field_size - 1, count);
    }
    // 우
    if ((y + 1 < field_size) && (field[x][y + 1] != 0) && (field_ID[x][y + 1] == 0))
    {
        Marking(x, y + 1, count);
    }
    else if ((y == field_size - 1) && (field[x][0] != 0) && (field_ID[x][0] == 0))
    {
        Marking(x, 0, count);
    }
}

/**
 * field를 탐색하면서 같은 빙하들끼리 같은 id로 marking해서 field_ID를 채우고
 * 총 빙하의 수를 return하는 함수
 */
int MarkingFieldID()
{
    int count = 0; // 빙하 아이디 → 1-based
    vol_of_ice.clear();
    for (int i = 0; i < field_size; i++)
    {
        for (int j = 0; j < field_size; j++)
        {
            // 빙하가 있으면서 아직 marking이 안된 곳을 만나면 그 지점을 기준으로 탐색 시작
            if ((field[i][j] != 0) && (field_ID[i][j] == 0))
            {
                count++;
                Marking(i, j, count);
            }
        }
    }
    return count;
}

/**
 * 처음에 딱 한번만 호출되는 함수
 * N은 전체 바다의 가로 및 세로 길이를 의미한다.
 * M은 초기 상태 때, 빙하의 개수를 의미 한다.
 * mIceBlock[][] 에는 N x N 개의 숫자가 전달되며 각 좌표의 얼음덩어리 “높이” 에 대한 정보를 담고 있다.
 * 각 얼음덩어리의 높이는 최대 1000 이다.(빙하가 없는 칸에는 높이 0으로 표시)
 * mIceGroup[][] 에는 M x 3 개의 숫자가 전달되며
 * 각 3개의 숫자는, 각각 빙하의 "위치"에 해당되는 얼음덩어리에 대한 X, Y 축 좌표와, 그 빙하가 움직이는 방향 ( 0 : ↑, 1 : →, 2 : ↓, 3 : ←) 을 의미한다.
 */
void init(int N, int M, int mIceBlock[MAX_N][MAX_N], int mIceGroup[MAX_M][3])
{
    debug = true;
    if (debug)
    {
        cout << "==================== Init Start ====================" << endl;
    }

    // Clear
    field.clear();
    field_ID.clear();
    dir_of_ice.clear();
    vol_of_ice.clear();

    // Initialize
    field_size = N;
    num_of_ice = M;
    year = 0;
    field.resize(MAX_N, vector<int>(MAX_N, 0));
    field_ID.resize(MAX_N, vector<int>(MAX_N, 0));

    if (debug)
    {
        printfield();
        printfieldId();
    }

    for (int i = 0; i < field_size; i++)
    {
        for (int j = 0; j < field_size; j++)
        {
            field[i][j] = mIceBlock[i][j];
        }
    }
    MarkingFieldID();
    for (int i = 0; i < MAX_M; i++)
    {
        int x = mIceGroup[MAX_M][0];
        int y = mIceGroup[MAX_M][1];
        int dir = mIceGroup[MAX_M][2];
        dir_of_ice[field_ID[y][x]] = dir;
    }

    if (debug)
    {
        cout << "After init" << endl;
        printfield();
        printfieldId();
    }
}

/**
 * 마지막 빙하의 상태를 기준으로 1년이 지난 후 빙하의 상태를 반환한다.
 * 반환은 RESULT 구조체의 mheights 배열에 각 좌표의 얼음덩어리 “높이” 값을 저장한다.
 */
RESULT res;
RESULT oneYearLater()
{
    if (debug)
    {
        cout << "==================== OneYearLater Start ====================" << endl;
    }

    // prev 파일들에 일단 현재 상태 저장
    vector<vector<int>> prev_field = field;
    vector<vector<int>> prev_field_ID = field_ID;
    map<int, int> prev_dir_of_ice = dir_of_ice;

    // 1. 융해 먼저 수행
    for (int i = 0; i < field_size; i++)
    {
        for (int j = 0; j < field_size; j++)
        {
            // 높이가 0보다 큰 부분이 있으면 높이 1 감소
            if (field[i][j] > 0)
            {
                field[i][j] -= 1;

                // 1 감소시켰는데 높이가 0이 되면 field_ID도 삭제
                if (field[i][j] == 0)
                {
                    field_ID[i][j] = 0;
                }
            }
        }
    }

    return res;
}