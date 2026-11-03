# Air Traffic Control using Prim's Algorithm (DAA Mini Project)

Optimises the route network between airports with **Prim's minimum spanning tree algorithm**.
The edge weight combines the **distance** between airports, the **capacity** of both airports and the
**airspace congestion** of the corridor:

```
w(u, v) = K * distance(u, v) * (1 + congestion(u, v)) / sqrt(capacity(u) * capacity(v))
```

The MST connects all airports with the minimum total weight (V-1 corridors, no loops).
Time complexity: **O(E log V)** with a binary min-heap (E = V(V-1)/2 on the complete airport graph).

## Files
| File | Purpose |
|---|---|
| `prim_atc.py` | Prim's algorithm, weight model, baselines, delay/fuel simulation (Python) |
| `prim_atc.cpp` | Same algorithm in C++ (about 20x faster, see report) |
| `visualize.py` | Route map, sector occupancy heat-map, traffic-flow map, workflow chart |
| `analysis.py` | Scalability (10 to 1000 airports) and comparison with baselines |
| `data/sample_airports.csv` | Sample airport data (12 airports) |
| `results/` | Generated graphs and `scalability.csv` |

## Run
```bash
pip install -r requirements.txt
python prim_atc.py          # MST for 12 sample airports
python visualize.py         # figures -> results/
python analysis.py          # scalability + comparison -> results/
g++ -O2 -std=c++17 -o prim_atc prim_atc.cpp && ./prim_atc 1000
```

## Results (simulation, 1000 airports)
* Delay: **5513 min** (Prim ATC) vs 98559 min (random tree) and 79603 min (single-hub star), about 94% / 93% lower.
* Compared with a distance-only MST, Prim ATC uses about 3% more delay but about 16% lower mean congestion
  and 33% lower peak airport utilisation.
* Runtime: Python 2.7 s, C++ 0.12 s for 1000 airports.

## Upload to GitHub
```bash
git init
git add .
git commit -m "Air Traffic Control using Prim's Algorithm (DAA mini project)"
git branch -M main
git remote add origin https://github.com/<your-username>/air-traffic-control.git
git push -u origin main
```
