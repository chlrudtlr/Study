#include <iostream>
#include <fstream>
#include <string>
#include <algorithm>
#include <cctype>
#include <vector>

using namespace std;

// 소문자 변환
string ToLower(string s) {
    transform(s.begin(), s.end(), s.begin(),
              [](unsigned char c) { return tolower(c); });
    return s;
}

// 앞뒤 공백 제거
string Trim(const string& s) {
    size_t start = s.find_first_not_of(" \t\r\n");
    if (start == string::npos) return "";

    size_t end = s.find_last_not_of(" \t\r\n");
    return s.substr(start, end - start + 1);
}

// 연속 공백/탭을 한 칸으로 압축
string NormalizeSpaces(const string& s) {
    string result;
    bool in_space = false;

    for (unsigned char c : s) {
        if (c == '\r') continue;

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

    return Trim(result);
}

// [시간] [T xxxx] [TC] prefix 제거
string RemoveLogPrefix(const string& line) {
    size_t tc_pos = line.find("[TC]");
    if (tc_pos != string::npos) {
        return Trim(line.substr(tc_pos + 4));
    }
    return Trim(line);
}

// 구분선(====...)인지 확인
bool IsSeparatorLine(const string& s) {
    string trimmed = Trim(s);
    if (trimmed.empty()) return true;

    for (char c : trimmed) {
        if (c != '=') return false;
    }
    return true;
}

// "Test Summary @@" 제목줄인지 확인
bool IsTestSummaryTitle(const string& s) {
    string lower = ToLower(NormalizeSpaces(s));
    return lower.find("test summary") != string::npos;
}

// Test Summary의 마지막 부분 확인
bool IsLastErrorLine(const string& s) {
    string lower = ToLower(NormalizeSpaces(s));
    return lower.find("the last error (the first failed thread)") != string::npos;
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
    bool in_summary_block = false;
    bool found_summary = false;

    string tc_name = "";
    vector<string> details;

    while (getline(fin, line)) {
        string content = RemoveLogPrefix(line);
        string normalized = NormalizeSpaces(content);

        // Test Summary 제목줄 발견
        if (IsTestSummaryTitle(content)) {
            in_summary_block = true;
            found_summary = true;
            continue;
        }

        if (!in_summary_block) {
            continue;
        }

        // prefix 제거 후 완전히 빈 줄이면 summary 끝
        if (Trim(content).empty()) {
            break;
        }

        // 구분선은 무시
        if (IsSeparatorLine(normalized)) {
            continue;
        }

        // summary block 안에서 정보성 없는 빈 줄은 무시
        if (normalized.empty()) {
            continue;
        }

        // 다음 섹션 시작처럼 보이면 종료할 수 있게 조건 추가 가능
        // 지금은 [TC] summary 이후 연속된 정보 라인들을 계속 수집

        // Test Case Name 추출
        string lower = ToLower(normalized);
        if (lower.find("test case name:") == 0 || lower.find("test case name :") == 0) {
            size_t pos = normalized.find(':');
            if (pos != string::npos) {
                tc_name = Trim(normalized.substr(pos + 1));
            }
        }

        details.push_back("- " + normalized);

        // The Last Error 줄이면 여기서 종료
        if (IsLastErrorLine(normalized)) {
            break;
        }
    }

    if (!found_summary) {
        cout << "__TC_NAME__\n";
        cout << "Unknown TC\n";
        cout << "__DETAILS__\n";
        cout << "Test Summary section not found.\n";
        cout << "__SUMMARY__\n";
        cout << "\n";
        return 0;
    }

    if (tc_name.empty()) {
        tc_name = "Unknown TC";
    }

    cout << "__TC_NAME__\n";
    cout << tc_name << "\n";
    cout << "__DETAILS__\n";
    for (const auto& item : details) {
        cout << item << "\n";
    }
    cout << "__SUMMARY__\n";
    cout << "\n";

    return 0;
}