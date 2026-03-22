#include <iostream>
#include <vector>

using namespace std;

void PrintVector(vector<int> v)
{
    cout << "Print vector : ";
    for (int i = 0; i < v.size(); i++)
    {
        cout << v[i] << " ";
    }
    cout << endl;
}

int main()
{
    vector<int> v = {1, 2, 3, 4, 5};
    cout << "===== Change size, capacity =====" << endl;
    PrintVector(v);
    cout << "Before size : " << v.size() << endl;
    v.resize(3);
    PrintVector(v);
    cout << "After size : " << v.size() << endl;

    return 0;
}