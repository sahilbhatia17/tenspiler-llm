#include <iostream>
#include <vector>
#include <chrono>

#include "random.h"

using namespace std;
using namespace std::chrono;

vector<vector<float>> a = random_matrix();
vector<vector<float>> b = random_matrix();

vector<vector<float>> multiply_blend_8(vector<vector<float>> base, vector<vector<float>> active) {
    vector<vector<float>> out;
    int m = base.size();
    int n = base[0].size();
    for (int row = 0; row < m; row++) {
        vector<float> row_vec;
		for (int col = 0; col < n; col++) {
            float pixel = (base[row][col] * active[row][col]) / 255;
			row_vec.push_back(pixel);
		}
		out.push_back(row_vec);
	}
	return out;
}

int main() {
    vector<long long> times;
    for (int i = 0; i < 10; i++) {
        auto start_time = high_resolution_clock::now();
        multiply_blend_8(a, b);
        auto end_time = high_resolution_clock::now();
        auto duration = duration_cast<microseconds>(end_time - start_time);
        times.push_back(duration.count());
    }


    cout << "Execution Time: " << average(times) << " microseconds +/-" << stdiv(times) << endl;
}