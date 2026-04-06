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
 */

#define MAX_N (100)
#define MAX_M (5000)

// 위에 선언되어 있어서 일단 주석처리 했음
// struct RESULT
// {
//     int heights[MAX_N][MAX_N];
// };

void init(int N, int M, int mIceBlock[MAX_N][MAX_N], int mIceGroup[MAX_M][3])
{
}

RESULT res;
RESULT oneYearLater()
{
    return res;
}