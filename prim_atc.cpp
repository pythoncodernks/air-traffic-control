// Air Traffic Control - Prim's MST (C++ version, min-heap)
// Build: g++ -O2 -o prim_atc prim_atc.cpp   Run: ./prim_atc [N]
#include <bits/stdc++.h>
using namespace std;
struct Airport { double x, y; int cap; };
static const double K = 10.0;

double weightOf(const Airport& a, const Airport& b, double cong) {
    double d = hypot(a.x - b.x, a.y - b.y);
    return K * d * (1.0 + cong) / sqrt((double)a.cap * b.cap);
}

double primMST(const vector<Airport>& ap, const vector<vector<double>>& cg, vector<pair<int,int>>& out) {
    int n = ap.size();
    vector<bool> vis(n, false);
    typedef tuple<double,int,int> T;
    priority_queue<T, vector<T>, greater<T>> pq;
    pq.emplace(0.0, 0, -1);
    double total = 0;
    while (!pq.empty()) {
        auto [w, u, p] = pq.top(); pq.pop();
        if (vis[u]) continue;
        vis[u] = true;
        if (p != -1) { out.push_back({p, u}); total += w; }
        for (int v = 0; v < n; v++)
            if (!vis[v]) pq.emplace(weightOf(ap[u], ap[v], cg[u][v]), v, u);
    }
    return total;
}

int main(int argc, char** argv) {
    int n = argc > 1 ? atoi(argv[1]) : 12;
    mt19937 rng(42);
    uniform_real_distribution<double> pos(0, 2000), cg(0, 0.5);
    int caps[] = {20, 30, 40, 60, 80, 100};
    vector<Airport> ap(n);
    for (auto& a : ap) { a.x = pos(rng); a.y = pos(rng); a.cap = caps[rng() % 6]; }
    vector<vector<double>> C(n, vector<double>(n, 0));
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) C[i][j] = C[j][i] = cg(rng);
    vector<pair<int,int>> mst;
    auto t0 = chrono::high_resolution_clock::now();
    double total = primMST(ap, C, mst);
    auto t1 = chrono::high_resolution_clock::now();
    printf("Airports: %d  MST edges: %zu  total weight: %.2f  time: %.3f ms\n", n, mst.size(), total,
           chrono::duration<double, milli>(t1 - t0).count());
    return 0;
}
