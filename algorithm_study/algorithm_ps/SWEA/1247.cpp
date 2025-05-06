// 1247.최적 경로 
// https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AV15OZ4qAPICFAYD

#include <iostream>
#include <vector>
#include <cstdlib> //abs
#include <algorithm> //min

using namespace std;

pair<int, int> home;
pair<int, int> company;
vector<pair<int, int>> pos; // 0:company 1~n: customer
vector<int> path;
vector<bool> visited;
int num_of_customer;
int min_dist;
int temp_dist;

void printPath(){
    cout << "Path : ";
    for(int i = 0; i < path.size(); i++){
        cout << "(" << pos[path[i]].first << ", " << pos[path[i]].second << ")" << " ";
    }
    cout << " / current min dist : " << min_dist;
    cout << endl;
}

void DFS(int start){
    path.push_back(start);
    visited[start] = true;

    int d = 0;
    if(path.size() > 1){
        int u = path[path.size() - 2];
        int v = path[path.size() - 1];
        d = abs(pos[u].first  - pos[v].first) + abs(pos[u].second - pos[v].second);
        temp_dist += d;
        if(temp_dist > min_dist){
            temp_dist -= d;
            path.pop_back();
            visited[start] = false;
            return;
        }
    }

    int to_home_dist = 0;
    if(path.size() == num_of_customer + 1){
        int last = path.back();
        to_home_dist = abs(pos[last].first  - home.first) + abs(pos[last].second - home.second);
        temp_dist += to_home_dist;
        min_dist = min(min_dist, temp_dist);
        // printPath();
    }
    else{
        for(int i = 1; i <= num_of_customer; i++){
            if(visited[i] == false){
                DFS(i);
            }
        }
    }

    temp_dist -= (d + to_home_dist);
    visited[start] = false;
    path.pop_back();
}

int main(int argc, char** argv)
{
	int test_case;
	int T;
	cin >> T;
	for(test_case = 1; test_case <= T; ++test_case)
	{
        pos.clear();
        visited.clear();
        path.clear();
        temp_dist = 0;
        min_dist = 987654321;

        cin >> num_of_customer;
        cin >> company.first >> company.second >> home.first >> home.second;

        pair<int, int> p;
        pos.resize(num_of_customer + 1, p);
        visited.resize(num_of_customer + 1, false);
        
        pos[0] = company;
        for(int i = 1; i <= num_of_customer; i++){
            cin >> pos[i].first >> pos[i].second;
        }

        DFS(0);
        cout << "#" << test_case << " " << min_dist << endl;
	}
	return 0;
}