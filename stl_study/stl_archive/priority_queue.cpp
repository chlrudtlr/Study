#include <iostream>
#include <queue>
#include <vector>
#include <functional> // greater

using namespace std;

int main() {
    // ✅ 기본 선언: 최대 힙 (내림차순 정렬, 가장 큰 값이 top)
    priority_queue<int> maxPQ;
    maxPQ.push(5);
    maxPQ.push(2);
    maxPQ.push(8);
    maxPQ.push(1);

    cout << "✅ max-heap (기본): ";
    while (!maxPQ.empty()) {
        cout << maxPQ.top() << " "; // 8 5 2 1
        maxPQ.pop();
    }
    cout << endl;

    // ✅ 최소 힙 선언 (오름차순 정렬, 가장 작은 값이 top)
    priority_queue<int, vector<int>, greater<int>> minPQ;
    minPQ.push(5);
    minPQ.push(2);
    minPQ.push(8);
    minPQ.push(1);

    cout << "✅ min-heap: ";
    while (!minPQ.empty()) {
        cout << minPQ.top() << " "; // 1 2 5 8
        minPQ.pop();
    }
    cout << endl;

    // ✅ 문자열 우선순위 큐 (알파벳 순)
    priority_queue<string> strPQ;
    strPQ.push("banana");
    strPQ.push("apple");
    strPQ.push("cherry");

    cout << "✅ string max-heap: ";
    while (!strPQ.empty()) {
        cout << strPQ.top() << " "; // cherry banana apple
        strPQ.pop();
    }
    cout << endl;

    // ✅ 사용자 정의 구조체 우선순위 큐
    struct Task {
        int priority;
        string name;
        // 기본 정렬 기준: priority 큰 순서로 정렬
        bool operator<(const Task& other) const {
            return priority < other.priority;
        }
    };

    priority_queue<Task> taskPQ;
    taskPQ.push({2, "Email"});
    taskPQ.push({5, "Code"});
    taskPQ.push({1, "Lunch"});

    cout << "✅ custom struct max-heap (priority 기준): ";
    while (!taskPQ.empty()) {
        cout << taskPQ.top().name << "(" << taskPQ.top().priority << ") ";
        taskPQ.pop();
    }
    cout << endl;

    // ✅ 사용자 정의 비교 함수로 최소 힙 구현
    struct Compare {
        bool operator()(const Task& a, const Task& b) {
            return a.priority > b.priority; // 작은 값이 top이 되도록
        }
    };

    priority_queue<Task, vector<Task>, Compare> minTaskPQ;
    minTaskPQ.push({2, "Email"});
    minTaskPQ.push({5, "Code"});
    minTaskPQ.push({1, "Lunch"});

    cout << "✅ custom struct min-heap (priority 기준): ";
    while (!minTaskPQ.empty()) {
        cout << minTaskPQ.top().name << "(" << minTaskPQ.top().priority << ") ";
        minTaskPQ.pop();
    }
    cout << endl;

    return 0;
}
