#include <iostream>
#include <bitset>

using namespace std;

int main() {
    // ✅ 선언 및 초기화 (크기는 반드시 컴파일 타임 상수여야 함)
    bitset<8> b1;           // 00000000 (모든 비트 0)
    bitset<8> b2(5);        // 00000101 (정수로 초기화)
    bitset<8> b3(string("1101")); // 문자열로 초기화 → 00001101

    cout << "b1: " << b1 << endl;
    cout << "b2: " << b2 << endl;
    cout << "b3: " << b3 << endl;

    // ✅ 비트 단위 조작
    b1.set(0);     // 0번째 비트를 1로
    b1.set();      // 전체를 1로
    b1.reset(0);   // 0번째 비트를 0으로
    b1.reset();    // 전체를 0으로
    b1.flip(2);    // 2번째 비트 반전
    b1.flip();     // 전체 반전

    cout << "b1 after flip: " << b1 << endl;

    // ✅ 비트 정보 얻기
    cout << "b2[0]: " << b2[0] << endl;      // 1
    cout << "b2.count(): " << b2.count() << endl; // 1의 개수
    cout << "b2.any(): " << b2.any() << endl;     // 하나라도 1인가? true
    cout << "b2.none(): " << b2.none() << endl;   // 모두 0인가? false
    cout << "b2.all(): " << b2.all() << endl;     // 모두 1인가? false

    // ✅ 정수로 변환
    cout << "b2.to_ulong(): " << b2.to_ulong() << endl;   // 5
    cout << "b2.to_ullong(): " << b2.to_ullong() << endl; // 5

    // ✅ 연산자 오버로딩 (AND, OR, XOR, NOT)
    bitset<4> x(string("1100"));
    bitset<4> y(string("1010"));

    cout << "x:     " << x << endl;
    cout << "y:     " << y << endl;
    cout << "x & y: " << (x & y) << endl;  // 1000
    cout << "x | y: " << (x | y) << endl;  // 1110
    cout << "x ^ y: " << (x ^ y) << endl;  // 0110
    cout << "~x:    " << (~x) << endl;     // 0011

    // ✅ 쉬프트 연산도 가능
    bitset<4> z(string("0011"));
    cout << "z << 1: " << (z << 1) << endl; // 0110
    cout << "z >> 1: " << (z >> 1) << endl; // 0001

    return 0;
}
