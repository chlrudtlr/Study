// 1654. 랜선 자르기
// https://www.acmicpc.net/problem/1654
#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;
using ll = long long;

int main(){

    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    ll ans = 0;
    int k = 0;
    ll need_num = 0;
    cin >> k >> need_num;
    vector<ll> v(k);
    for(int i = 0; i < k; i++){
        cin >> v[i];
    }
    sort(v.rbegin(), v.rend());

    ll min = 1;
    ll max = v[0];
    ll mid = (min + max) / 2;

    while(min <= max){
        mid = (min + max) / 2;
        ll count = 0;
        for(int i = 0; i < k; i++){
            count += v[i] / mid;
        }
        if(count >= need_num){
            ans = mid;
            min = mid + 1;
        }
        else{
            max = mid - 1;
        }
    }

    cout << ans << endl;

    return 0;
}