#include <iostream>
#include <fstream>
#include <string>
#include <algorithm>
#include <cctype>

using namespace std;

// 소문자 변환
string ToLower(string s) {
    transform(s.begin(), s.end(), s.begin(),
              [](unsigned char c) { return tolower(c); });
    return s;
}

// 연속 공백/탭을 한 칸으로 압축
string NormalizeSpaces(const string& s) {
    string result;
    bool in_space = false;

    for (unsigned char c : s) {
        if (c == '\r') {
            continue;  // CR 제거
        }

        if (isspace(c)) {
            if (!in_space) {
                result += ' ';
                in_space = true;
            }
        } else {
            result += c;
            in_space = false;
        }
    }

    return result;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Usage: parser <input_file>" << endl;
        return 1;
    }

    ifstream fin(argv[1]);
    if (!fin.is_open()) {
        cerr << "Failed to open input file." << endl;
        return 1;
    }

    string line;
    bool found = false;

    while (getline(fin, line)) {
        string normalized = NormalizeSpaces(line);
        string lower_line = ToLower(normalized);

        // 대소문자 무시 + 공백 정규화 후 검색
        if (lower_line.find("test summary") != string::npos) {
            cout << line << '\n';   // 원본 라인 그대로 출력
            found = true;
        }
    }

    if (!found) {
        cout << "No lines containing \"Test Summary\" were found." << endl;
    }

    return 0;
}