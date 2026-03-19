#include <iostream>
#include <string>
#include <algorithm>

using namespace std;

int main() {
    // ✅ 문자열 선언 및 초기화
    string s1 = "Hello";
    string s2("World");
    string s3 = s1 + " " + s2; // 문자열 덧셈 가능
    cout << "s3: " << s3 << endl;

    // ✅ 문자열 길이
    cout << "Length: " << s3.length() << endl;

    // ✅ 문자 접근
    cout << "First char: " << s3[0] << endl;
    cout << "Last char: " << s3.back() << endl;

    // ✅ 부분 문자열 추출
    string sub = s3.substr(0, 5); // 시작 인덱스, 길이
    cout << "substr: " << sub << endl;

    // ✅ 문자열 비교
    cout << (s1 == "Hello" ? "Equal" : "Not Equal") << endl;

    // ✅ 문자열 삽입
    string s4 = "C++";
    s4.insert(1, " is fun "); // 1번 인덱스에 삽입
    cout << "After insert: " << s4 << endl;

    // ✅ 문자열 삭제
    s4.erase(1, 7); // 1번 인덱스부터 7개 제거
    cout << "After erase: " << s4 << endl;

    // ✅ 문자열 뒤집기
    reverse(s1.begin(), s1.end());
    cout << "Reversed: " << s1 << endl;

    // ✅ 문자열 검색
    string text = "hello cpp world cpp!";
    size_t pos = text.find("cpp");
    if (pos != string::npos)
        cout << "'cpp' found at: " << pos << endl;

    // ✅ 문자열 여러 번 찾기
    cout << "All 'cpp' positions: ";
    size_t start = 0;
    while ((pos = text.find("cpp", start)) != string::npos) {
        cout << pos << " ";
        start = pos + 1;
    }
    cout << endl;

    // ✅ 문자열 치환
    string replace_str = "abcabcabc";
    replace_str.replace(replace_str.find("abc"), 3, "XYZ");
    cout << "After replace: " << replace_str << endl;

    // ✅ 문자열 to int / int to string
    string numStr = "123";
    int num = stoi(numStr);
    cout << "num + 1: " << num + 1 << endl;

    int n = 456;
    string nStr = to_string(n);
    cout << "nStr + \"7\": " << nStr + "7" << endl;

    // ✅ 문자열 전체 대문자 변환
    string upperStr = "hello";
    transform(upperStr.begin(), upperStr.end(), upperStr.begin(), ::toupper);
    cout << "Uppercase: " << upperStr << endl;

    // ✅ 문자열 전체 소문자 변환
    string lowerStr = "WORLD";
    transform(lowerStr.begin(), lowerStr.end(), lowerStr.begin(), ::tolower);
    cout << "Lowercase: " << lowerStr << endl;

    return 0;
}
