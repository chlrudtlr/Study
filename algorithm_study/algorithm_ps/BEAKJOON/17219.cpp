#include <iostream>
#include <map>

using namespace std;

int main() {
    cin.tie(NULL);
    ios::sync_with_stdio(false);

    int num_of_site = 0;
    int num_to_find = 0;
    cin >> num_of_site >> num_to_find;

    map<string, string> m;

    for (int i = 0; i < num_of_site; i++) {
        string site = "", pw = "";
        cin >> site >> pw;
        m[site] = pw;
    }

    for (int i = 0; i < num_to_find; i++) {
        string site = "";
        cin >> site;
        cout << m[site] << endl;
    }

    return 0;
}