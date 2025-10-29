class Solution {
public:
    int diameter(int V, vector<vector<int>>& edges) {
        vector<vector<int>> adj(V);
        for (auto& e : edges) {
            adj[e[0]].push_back(e[1]);
            adj[e[1]].push_back(e[0]);
        }
        auto bfs = [&](int src) {
            vector<int> d(V, -1);
            queue<int> q;
            q.push(src);
            d[src] = 0;
            int far = src, maxD = 0;
            while (!q.empty()) {
                int u = q.front();
                q.pop();
                for (int v : adj[u]) {
                    if (d[v] == -1) {
                        d[v] = d[u] + 1;
                        q.push(v);
                        if (d[v] > maxD) {
                            maxD = d[v];
                            far = v;
                        }
                    }
                }
            }
            return make_pair(far, maxD);
        };
        auto [end1, _] = bfs(0);
        auto [end2, diam] = bfs(end1);
        return diam;
    }
};