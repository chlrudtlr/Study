#include <iostream>
#include <vector>

using namespace std;

vector<vector<int>> v;
vector<int> path;
vector<bool> visited;

void DFS(int start){
    path.push_back(start);
    visited[start] = true;

    bool check_remain_node = false;
    for(int i = 0; i < v[start].size(); i++){
        if((v[start][i] == 1) && (!visited[i])){
            check_remain_node = true;
            DFS(i);
        }
    }

    if(!check_remain_node){
        cout << "Path : ";
        for(int i = 0; i < path.size(); i++){
            cout << path[i] << " ";
        }
        cout << endl;
    }

    path.pop_back();
    visited[start] = false;
}

int main(){
    vector<int> temp;
    temp.resize(13, 0); // node가 1 ~ 12 이므로 13으로 세팅팅
    v.resize(13, temp);

    visited.resize(13, false);

    // 구조
    //           1
    //        /  |  \
    //       2   3   4
    //      / \  |   |\
    //     5   6 7   8 9
    //           |\     \
    //          10 11   12

    v[1][2] = 1;
    v[2][1] = 1;

    v[1][3] = 1;
    v[3][1] = 1;

    v[1][4] = 1;
    v[4][1] = 1;

    v[2][5] = 1;
    v[5][2] = 1;

    v[2][6] = 1;
    v[6][2] = 1;

    v[3][7] = 1;
    v[7][3] = 1;

    v[4][8] = 1;
    v[8][4] = 1;

    v[4][9] = 1;
    v[9][4] = 1;

    v[7][10] = 1;
    v[10][7] = 1;

    v[7][11] = 1;
    v[11][7] = 1;

    v[9][12] = 1;
    v[12][9] = 1;

    DFS(1);

    return 0;
}