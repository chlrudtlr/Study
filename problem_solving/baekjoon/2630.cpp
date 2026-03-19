#include <iostream>
#include <queue>
#include <vector>

using namespace std;

int arr[130][130];
int count0;
int count1;

void CheckSameColor(int x, int y, int size) {
    // cout << "Check : (" << x << "," << y << ") = 0 / size = " << size << endl;
    int first_color = arr[y][x];

    if (size == 1) {
        if (first_color == 0) {
            // cout << "(" << x << "," << y << ") = 0 / size = " << size << endl;
            count0++;
        } else {  // first_color == 1
            // cout << "(" << x << "," << y << ") = 1 / size = " << size << endl;
            count1++;
        }
        return;
    }

    for (int i = y; i < y + size; i++) {
        for (int j = x; j < x + size; j++) {
            if (arr[i][j] != first_color) {
                CheckSameColor(x, y, size / 2);
                CheckSameColor(x + size / 2, y, size / 2);
                CheckSameColor(x, y + size / 2, size / 2);
                CheckSameColor(x + size / 2, y + size / 2, size / 2);
                return;
            }
        }
    }

    if (first_color == 0) {
        // cout << "(" << x << "," << y << ") = 0 / size = " << size << endl;
        count0++;
    } else {  // first_color == 1
        // cout << "(" << x << "," << y << ") = 1 / size = " << size << endl;
        count1++;
    }

    return;
}

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(NULL);
    std::cout.tie(NULL);

    count0 = 0;
    count1 = 0;
    int size = 0;
    cin >> size;
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            cin >> arr[i][j];
        }
    }

    CheckSameColor(0, 0, size);

    cout << count0 << '\n';
    cout << count1 << '\n';

    return 0;
}