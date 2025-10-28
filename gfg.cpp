class Solution {
public:
    vector<vector<int>> kSmallestPair(vector<int> &arr1, vector<int> &arr2, int k) {
        vector<vector<int>> res;
        priority_queue<pair<int,pair<int,int>>, vector<pair<int,pair<int,int>>>, greater<>> pq;
        for(int i = 0; i < min((int)arr1.size(), k); i++) pq.push({arr1[i] + arr2[0], {i, 0}});
        while(k-- && !pq.empty()) {
            auto [sum, idx] = pq.top(); pq.pop();
            auto [i, j] = idx;
            res.push_back({arr1[i], arr2[j]});
            if(j + 1 < arr2.size()) pq.push({arr1[i] + arr2[j + 1], {i, j + 1}});
        }
        return res;
    }
};