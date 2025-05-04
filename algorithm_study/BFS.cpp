#include <iostream>
#include <vector>
#include <queue>

using namespace std;

vector<vector<int>> v;
queue<int> path;
vector<bool> visited;

void BFS(int start){
    path.push(start);
    visited[start] = true;

    while(!path.empty()){
        int node = path.front();
        cout << node << " ";
        path.pop();
        for(int i = 0; i < v[node].size(); i++){
            if((v[node][i] == 1) && (visited[i] == false)){
                visited[i] = true;
                path.push(i);
            }
        }
    }
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

    BFS(1);
    cout << endl;

    return 0;
}