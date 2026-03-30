/**
 * @brief priority queue 연습
 */
#include <iostream>
#include <vector>
#include <queue>

using namespace std;

int main()
{
    cout << "===== 가장 기본적인 사용법 =====" << endl;
    priority_queue<int> pq;
    pq.push(4);
    pq.push(2);
    pq.push(5);
    pq.push(1);
    pq.push(3);

    cout << "자동으로 내림차순 정렬 : ";
    while (!pq.empty())
    {
        cout << pq.top() << " ";
        pq.pop();
    }
    cout << endl;

    cout << "그런데 만약 오름차순으로 정리하고 싶다면?" << endl;

    priority_queue<int, vector<int>, greater<int>> pq1;
    pq1.push(4);
    pq1.push(2);
    pq1.push(5);
    pq1.push(1);
    pq1.push(3);

    cout << "이런식으로 하면 오름차순으로 정렬 : ";
    while (!pq1.empty())
    {
        cout << pq1.top() << " ";
        pq1.pop();
    }
    cout << endl;
    cout << endl;

    cout << "===== 원소가 2개인 경우 사용법(1) : pair 사용 =====" << endl;
    priority_queue<pair<int, int>> pq2;
    pq2.push(make_pair(4, 2));
    pq2.push(make_pair(1, 1));
    pq2.push(make_pair(5, 3));
    pq2.push(make_pair(3, 2));
    pq2.push(make_pair(2, 5));

    cout << "첫 번째 원소 기준으로 내림차순 정렬 : ";
    while (!pq2.empty())
    {
        cout << "(" << pq2.top().first << ", " << pq2.top().second << ")" << " ";
        pq2.pop();
    }
    cout << endl;

    cout << "그런데 만약 첫 번째 원소가 같으면?" << endl;
    cout << "두 번째 원소 기준 내림차순 : ";
    pq2.push(make_pair(5, 1));
    pq2.push(make_pair(4, 2));
    pq2.push(make_pair(1, 1));
    pq2.push(make_pair(5, 2));
    pq2.push(make_pair(5, 3));
    while (!pq2.empty())
    {
        cout << "(" << pq2.top().first << ", " << pq2.top().second << ")" << " ";
        pq2.pop();
    }
    cout << endl;

    return 0;
}