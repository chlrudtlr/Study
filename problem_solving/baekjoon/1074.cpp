// 1074. Z
// https://www.acmicpc.net/problem/1074
#include <iostream>
#include <cmath>

using namespace std;

int field_size;
int N = 0, r = 0, c = 0;
bool start;

int getQuadrant(int size, int x, int y)
{
    start = true; // 처음에 해당 함수를 탔음을 표시
    // size는 한 변의 길이. 즉 N이 3이면 2^3=8이 된다.
    int pivot = size / 2;
    if (x >= pivot && y < pivot)
    {
        return 1;
    }
    else if (x < pivot && y < pivot)
    {
        return 2;
    }

    else if (x < pivot && y >= pivot)
    {
        return 3;
    }

    else if (x >= pivot && y >= pivot)
    {
        return 4;
    }
    return 0;
}

int main()
{
    // 1 ≤ N ≤ 15
    // 0 ≤ r, c < 2^N
    // r행 c열을 몇 번째로 방문했는지 출력
    cin >> N >> r >> c;
    field_size = pow(2, N); // field_size는 한변의 길이
    start = false;

    int res = 0;
    while (true)
    {
        int quadrant = getQuadrant(field_size, c, r);
        int base = (field_size / 2) * (field_size / 2);

        // 2사분면일 때에는 계산할 필요 없음
        if (quadrant == 1)
        {
            res += base;
            if (!start)
                res -= 1;
            c -= field_size / 2;
        }
        else if (quadrant == 3)
        {
            res += base * 2;
            if (!start)
                res -= 1;
            r -= field_size / 2;
        }

        else if (quadrant == 4)
        {
            res += base * 3;
            if (!start)
                res -= 1;
            c -= field_size / 2;
            r -= field_size / 2;
        }

        // cout << "중간점검 : " << res << endl;

        field_size /= 2;

        if (field_size == 1)
        {
            break;
        }
    }

    cout << res << endl;
    return 0;
}