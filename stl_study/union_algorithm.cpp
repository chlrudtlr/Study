#include <iostream>
#include <vector>

using namespace std;

int node_num = 10;
vector<int> parent(node_num, 0);
vector<int> node_rank(node_num, 0);

void PrintVector()
{
    cout << "Parent: ";
    for (int i = 0; i < parent.size(); i++)
    {
        cout << "(" << i << ", " << parent[i] << ")";
    }
    cout << endl;

    cout << "Rank: ";
    for (int i = 0; i < node_rank.size(); i++)
    {
        cout << "(" << i << ", " << node_rank[i] << ")";
    }
    cout << endl;
}

int FindParent(int k)
{
    if (parent[k] == k)
    {
        return k;
    }
    else
    {
        int parentK = parent[k];
        return FindParent(parentK);
    }
}

void Union(int a, int b)
{
    int parentA = FindParent(a);
    int parentB = FindParent(b);

    if (parentA == parentB)
    {
        return;
    }
    else
    {
        if (node_rank[parentA] < node_rank[parentB])
        {
            parent[parentA] = parentB;
        }
        else if (node_rank[parentA] > node_rank[parentB])
        {
            parent[parentB] = parentA;
        }
        else // node_rank[parentA] == node_rank[parentB]
        {
            parent[parentA] = parentB;
            node_rank[parentA]++;
        }
    }
}

int main()
{
    // Init parent, node_rank
    for (int i = 0; i < node_num; i++)
    {
        parent[i] = i;
    }
    cout << "Init" << endl;
    PrintVector();

    // Union
    Union(0, 1);
    PrintVector();

    Union(2, 3);
    PrintVector();

    Union(6, 8);
    PrintVector();

    Union(1, 3);
    PrintVector();

    return 0;
}