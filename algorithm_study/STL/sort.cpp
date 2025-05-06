#include <iostream>
#include <algorithm>

using namespace std;

void printArr(int* arr)
{
    cout<<"arr : ";
    for(int i=0;i<10;i++){
        cout<<arr[i]<<" ";
    }
    cout<<endl;
}

bool compare(int a, int b)
{
    return a>b;
}

int main()
{
    int arr[10]={4,1,3,8,0,6,9,7,2,5};
    sort(arr, arr+10);
    printArr(arr);
    sort(arr, arr+10, compare);
    printArr(arr);

    return 0;
}
