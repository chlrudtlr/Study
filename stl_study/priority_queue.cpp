/**
 * @brief priority queue 연습
 */
#include <iostream>
#include <vector>
#include <queue>

using namespace std;

struct cmp1
{
    bool operator()(pair<int, int> a, pair<int, int> b)
    {
        if (a.first == b.first)
            return a.second > b.second; // second 오름차순
        return a.first < b.first;       // first 내림차순
    }
};

struct cmp2
{
    bool operator()(pair<int, int> a, pair<int, int> b)
    {
        if (a.first == b.first)
            return a.second > b.second; // second 오름차순
        return a.first > b.first;       // first 내림차순
    }
};

struct Node
{
    int a, b, c;

    bool operator<(const Node &other) const
    {
        if (a != other.a)
            return a > other.a; // a 오름차순
        if (b != other.b)
            return b < other.b; // b 내림차순
        return c > other.c;     // c 오름차순
    }
};

int main()
{
    cout << "===== 가장 기본적인 사용법 =====" << endl;
    priority_queue<int> pq;
    pq.push(4);
    pq.push(2);
    pq.push(5);
    pq.push(1);
    pq.push(3);

    cout << "▶ 자동으로 내림차순 정렬 : ";
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

    cout << "▶ 이런 식으로 하면 오름차순으로 정렬 : ";
    while (!pq1.empty())
    {
        cout << pq1.top() << " ";
        pq1.pop();
    }
    cout << endl;
    cout << endl;

    cout << "===== 원소가 2개인 경우 사용법 : pair 사용 =====" << endl;
    priority_queue<pair<int, int>> pq2;
    pq2.push(make_pair(4, 2));
    pq2.push(make_pair(1, 1));
    pq2.push(make_pair(5, 3));
    pq2.push(make_pair(3, 2));
    pq2.push(make_pair(2, 5));

    cout << "▶ 첫 번째 원소 기준으로 내림차순 정렬 : ";
    while (!pq2.empty())
    {
        cout << "(" << pq2.top().first << ", " << pq2.top().second << ")" << " ";
        pq2.pop();
    }
    cout << endl;

    cout << "그런데 만약 첫 번째 원소가 같으면?" << endl;
    cout << "▶ 두 번째 원소 기준 내림차순 : ";
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
    cout << endl;

    cout << "그럼 이제 이런 생각이 듭니다." << endl;
    cout << "첫 번째 원소는 내림차순으로, (첫 번째 원소가 같은 애들은)두 번째 원소는 오름차순으로 정렬하고 싶다!" << endl;
    cout << "그럴 때에는 comparator를 직접 커스텀해서 사용해야 한다." << endl;

    cout << "▶ 첫 번째 원소는 내림차순, 두 번째 원소는 오름차순 : ";
    priority_queue<pair<int, int>, vector<pair<int, int>>, cmp1> pq3;
    pq3.push(make_pair(5, 1));
    pq3.push(make_pair(4, 2));
    pq3.push(make_pair(1, 1));
    pq3.push(make_pair(5, 2));
    pq3.push(make_pair(5, 3));
    while (!pq3.empty())
    {
        cout << "(" << pq3.top().first << ", " << pq3.top().second << ")" << " ";
        pq3.pop();
    }
    cout << endl;

    cout << "comparator를 잘 정의하면 다음과 같이 첫 번째 원소, 두 번쨰 원소 둘 다 오름차순도 가능" << endl;
    cout << "▶ 첫 번째 원소랑 두 번째 원소 둘 다 오름차순 : ";
    priority_queue<pair<int, int>, vector<pair<int, int>>, cmp2> pq4;
    pq4.push(make_pair(5, 1));
    pq4.push(make_pair(4, 2));
    pq4.push(make_pair(1, 1));
    pq4.push(make_pair(5, 2));
    pq4.push(make_pair(5, 3));
    while (!pq4.empty())
    {
        cout << "(" << pq4.top().first << ", " << pq4.top().second << ")" << " ";
        pq4.pop();
    }
    cout << endl;
    cout << endl;

    cout << "근데 원소의 갯수가 3, 4개 막 이렇게 많아지면 이 방법은 못 쓰니까 다른 방법을 알아보자" << endl;

    cout << endl;

    cout << "===== 원소가 여러 개인 경우 사용법 : 구조체 사용 =====" << endl;
    cout << "원소의 갯수가 3개라고 가정하고 구조체 Node를 만들어보자" << endl;
    cout << "첫번째 원소부터 차례로 오름차순, 내림차순, 오름차순 기준 : ";
    priority_queue<Node> pq5;
    pq5.push({1, 2, 3});
    pq5.push({1, 5, 1});
    pq5.push({1, 5, 2});
    pq5.push({2, 1, 1});
    while (!pq5.empty())
    {
        cout << "(" << pq5.top().a << ", " << pq5.top().b << ", " << pq5.top().c << ")" << " ";
        pq5.pop();
    }
    cout << endl;

    return 0;
}