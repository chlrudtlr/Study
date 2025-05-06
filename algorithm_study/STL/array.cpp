#include <iostream>
#include <cstring>      // memset, memcpy
#include <algorithm>    // fill, copy, equal, swap_ranges
#include <numeric>      // iota

using namespace std;

int main() {
    // ✅ C 스타일 배열
    int arr[10];

    // ✅ memset: 바이트 단위로 초기화 (0, -1만 권장)
    memset(arr, 0, sizeof(arr)); // 모든 값을 0으로 초기화
    cout << "memset to 0: ";
    for (int i : arr) cout << i << " ";
    cout << endl;

    // ⚠️ 경고: memset(arr, 1, sizeof(arr)) → 1이 아닌 이상한 값이 들어감 (1바이트 단위 처리)

    // ✅ STL fill: 배열에 특정 값 채우기
    fill(arr, arr + 10, 7); // 모든 값 7
    cout << "fill to 7: ";
    for (int i : arr) cout << i << " ";
    cout << endl;

    // ✅ iota: 연속된 숫자 채우기 (0부터)
    iota(arr, arr + 10, 0); // 0~9 채움
    cout << "iota: ";
    for (int i : arr) cout << i << " ";
    cout << endl;

    // ✅ memcpy: 배열 복사
    int arr2[10];
    memcpy(arr2, arr, sizeof(arr));
    cout << "memcpy: ";
    for (int i : arr2) cout << i << " ";
    cout << endl;

    // ✅ STL copy: 배열 복사
    int arr3[10];
    copy(arr, arr + 10, arr3);
    cout << "copy: ";
    for (int i : arr3) cout << i << " ";
    cout << endl;

    // ✅ equal: 배열 비교
    cout << "arr2 == arr3? " << (equal(arr2, arr2 + 10, arr3) ? "Yes" : "No") << endl;

    // ✅ memcmp: 바이트 비교
    cout << "memcmp(arr2, arr3)? " << (memcmp(arr2, arr3, sizeof(arr2)) == 0 ? "Equal" : "Different") << endl;

    // ✅ swap_ranges: 두 배열 swap
    int arr4[10];
    fill(arr4, arr4 + 10, 100);
    swap_ranges(arr3, arr3 + 10, arr4);
    cout << "after swap_ranges:\n";
    cout << "arr3: ";
    for (int i : arr3) cout << i << " ";
    cout << "\narr4: ";
    for (int i : arr4) cout << i << " ";
    cout << endl;

    return 0;
}
