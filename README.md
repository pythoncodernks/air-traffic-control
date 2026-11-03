# Air Traffic Control Using Prim's Minimum Spanning Tree Algorithm

### Design and Analysis of Algorithms (DAA) — Academic Mini Project

[![Language](https://img.shields.io/badge/Language-Python%203%20%7C%20C%2B%2B17-1e3a8a.svg)](https://www.python.org)
[![Algorithm](https://img.shields.io/badge/Algorithm-Prim's%20MST-2563eb.svg)](https://en.wikipedia.org/wiki/Prim%27s_algorithm)
[![Complexity](https://img.shields.io/badge/Time-O(E%20log%20V)-0284c7.svg)](#5-complexity-analysis)
[![Verified](https://img.shields.io/badge/Verified%20vs-NetworkX%20Kruskal-15803d.svg)](#11-testing-and-verification)

---

## 1. Project Objective

The objective of this project is to design, implement and analyse an **air-route optimisation system** that connects a set of airports with the minimum combined cost, using **Prim's minimum spanning tree (MST) algorithm**.

The cost of a corridor between two airports depends on three factors: the **distance** between them, the **capacity** of both airports and the **congestion** of the airspace in between. This is an **algorithmic demonstration and analysis project** for college coursework in DAA. The project focuses on:

- Modelling airports and corridors as a weighted graph.
- A weight function that combines distance, capacity and congestion.
- A heap-based implementation of Prim's algorithm in **Python** and **C++**.
- Visualisation of routes, sector occupancy and traffic-flow patterns.
- Measuring delay, fuel, congestion and airport utilisation, and comparing with baseline networks.
- Scalability analysis from 10 to 1000 airports.

---

## 2. Problem Statement

Let $A = \{a_1, \dots, a_n\}$ be a set of $n$ airports. Airport $a_i$ has a position $(x_i, y_i)$ in km and a capacity $cap_i$ (flights per hour). Between every pair of airports there is a candidate corridor with a congestion factor $c_{ij} \in [0, 0.5]$.

Find a **spanning tree** $T$ (a set of $n-1$ corridors that connects all airports with no cycles) such that the total weight $\sum_{e \in T} w(e)$ is minimum.

| Factor | Modelled as | Effect on corridor weight |
|---|---|---|
| Distance | Euclidean distance $d(u,v)$ in km | Longer corridor, higher weight |
| Airport capacity | $cap(u)$, $cap(v)$ | Higher capacity, lower weight |
| Airspace congestion | Factor $c(u,v)$ | More congestion, higher weight |

Checking all $n^{n-2}$ spanning trees (Cayley's formula) is impossible even for 20 airports, so an efficient algorithm is required.

---

## 3. Algorithm Explanation: Prim's Algorithm

Prim's algorithm is a **greedy** algorithm. It starts from one airport and grows a tree; in every step it adds the cheapest corridor that connects an airport inside the tree to an airport outside it. By the **cut property** of MSTs, the cheapest edge crossing any cut belongs to some MST, so every greedy choice is safe and the final tree is optimal.

### Edge Weight Model

$$w(u,v) = K \cdot d(u,v) \cdot (1 + c(u,v)) \; / \; \sqrt{cap(u) \cdot cap(v)}, \quad K = 10$$

Example: a 500 km corridor between two airports of capacity 100 and no congestion has weight $10 \cdot 500 / 100 = 50$; between two airports of capacity 20 it has weight 250, and with congestion 0.5 it rises to 375.

### Algorithmic Execution Steps

1. **Initialise:** mark all airports as not visited; push `(0, start, none)` into a min-heap.
2. **Extract minimum:** pop the cheapest entry `(w, u, parent)`.
3. **Skip if visited:** if `u` is already in the tree, discard the entry (lazy deletion).
4. **Add to tree:** mark `u` visited and add the corridor `(parent, u)` to the MST.
5. **Relax:** for every airport `v` not in the tree, push `(w(u, v), v, u)` into the heap.
6. **Repeat** until $V-1$ corridors are selected.

---

## 4. Prim's Pseudocode

```
Algorithm: PRIM-ATC(airports, congestion, start)
Input : n airports (x, y, capacity) and congestion factor for every pair
Output: list of n-1 corridors (MST) and its total weight

visited[0..n-1] = false;  MST = [];  total = 0
heap = { (0, start, none) }
while heap is not empty:
    (w, u, parent) = EXTRACT-MIN(heap)
    if visited[u]: continue
    visited[u] = true
    if parent != none: MST.add((parent, u, w)); total += w
    for each airport v with visited[v] == false:
        c = congestion(u, v)
        INSERT(heap, (K*dist(u,v)*(1+c)/sqrt(cap[u]*cap[v]), v, u))
return MST, total
```

---

## 5. Complexity Analysis

### Time Complexity

- On the complete airport graph $E = V(V-1)/2$. Each corridor is pushed and popped at most once, each costing $O(\log E) = O(\log V)$.
- **Time: $O(E \log V) = O(V^2 \log V)$.**
- For this dense graph the matrix version of Prim runs in $O(V^2)$ and is asymptotically faster; the heap version was used because it is the standard form for general graphs.

### Space Complexity

- **$O(E)$** in the worst case for the lazy heap, plus $O(V)$ for the visited array and the MST.

| Variant | Time |
|---|---|
| Adjacency matrix, linear scan | $O(V^2)$ |
| Binary heap, lazy deletion (used here) | $O(E \log V)$ |
| Binary heap, decrease-key | $O(E \log V)$ |
| Fibonacci heap | $O(E + V \log V)$ |

---

## 6. Simulation Model

> **Note:** the parameters below are **assumptions made for this simulation**, not measured real-world data.

| Quantity | Definition / value |
|---|---|
| Airspace and airports | 2000 km x 2000 km; capacity from {20, 30, 40, 60, 80, 100}; seed 42 |
| Congestion | Uniform random in [0, 0.5] per corridor; seed 7 |
| En-route delay | distance / 800 km/h x 60 x (1 + congestion) minutes |
| Airport queueing delay | 30 x degree / capacity minutes |
| Fuel | distance x 4.5 kg/km x (1 + congestion) |
| Airport utilisation (safety proxy) | degree / capacity (maximum over airports) |
| Baselines | Distance-only MST, random spanning tree (mean of 5), single-hub star |

Aircraft separation and collision avoidance are **not** simulated.

---

## 7. Visualisation

**Candidate corridors (left) and the Prim MST (right) for 25 airports**

![MST network](results/mst_network.png)

**Sector occupancy (4 x 4 sectors, route-km per sector)**

![Sector occupancy](results/sector_occupancy.png)

**Traffic-flow pattern (line width = airports served through the corridor)**

![Traffic flow](results/traffic_flow.png)

---

## 8. Results

### 8.1 Sample output (12 airports, `python prim_atc.py`)

| No. | From | To | Distance (km) | Cap. A | Cap. B | Weight |
|---|---|---|---|---|---|---|
| 1 | AP000 | AP003 | 98.8 | 40 | 20 | 46.3 |
| 2 | AP000 | AP006 | 434.1 | 40 | 80 | 90.78 |
| 3 | AP006 | AP008 | 389.0 | 80 | 30 | 96.0 |
| 4 | AP006 | AP005 | 991.7 | 80 | 100 | 142.72 |
| 5 | AP005 | AP011 | 201.1 | 100 | 100 | 29.96 |
| 6 | AP011 | AP002 | 224.1 | 100 | 20 | 64.69 |
| 7 | AP005 | AP007 | 643.8 | 100 | 30 | 148.4 |
| 8 | AP007 | AP009 | 246.2 | 30 | 20 | 134.07 |
| 9 | AP006 | AP001 | 621.5 | 80 | 20 | 172.73 |
| 10 | AP001 | AP010 | 316.1 | 20 | 40 | 133.93 |
| 11 | AP005 | AP004 | 804.4 | 100 | 20 | 208.12 |

Total weight: **1267.69** (11 corridors).

### 8.2 Delay and fuel (lower is better)

| Airports | Delay Prim (min) | Delay Distance-MST | Delay Random tree | Delay Star | Fuel Prim (kg) | Fuel Distance-MST (kg) |
|---|---|---|---|---|---|---|
| 50 | 1,066 | 978 | 4,832 | 4,011 | 60,642 | 54,343 |
| 200 | 2,176 | 2,019 | 19,920 | 16,165 | 116,535 | 103,317 |
| 1000 | 5,513 | 5,351 | 98,559 | 79,603 | 261,713 | 235,342 |

![Comparison](results/comparison.png)

### 8.3 Key findings (1000 airports)

- Delay is **94.4%** lower than a random tree and **93.1%** lower than a single-hub star.
- Compared with the **distance-only MST** (which is optimal for distance alone), Prim ATC uses about 3.0% more delay and 11.2% more fuel, but its routes have **15.7% lower mean congestion** (0.215 vs 0.255) and the busiest airport has **33.3% lower utilisation** (0.1 vs 0.15).

### 8.4 Scalability (run time)

| Airports (V) | Corridors (E) | Python (ms) | C++ (ms) | Speed-up |
|---|---|---|---|---|
| 10 | 45 | 0.099 | - | - |
| 25 | 300 | 0.27 | - | - |
| 50 | 1,225 | 1.229 | - | - |
| 100 | 4,950 | 5.451 | 0.925 | 5.9x |
| 200 | 19,900 | 29.333 | 4.129 | 7.1x |
| 400 | 79,800 | 229.039 | 19.121 | 12.0x |
| 600 | 179,700 | 672.788 | - | - |
| 800 | 319,600 | 1580.022 | 73.793 | 21.4x |
| 1000 | 499,500 | 2702.356 | 116.465 | 23.2x |

![Runtime](results/runtime.png)
![Normalised cost](results/complexity.png)

Run time grows polynomially with V, in line with $E = O(V^2)$. Time divided by $E \log V$ rises slowly (about 0.17 to 0.54 microseconds per unit between 100 and 1000 airports) because the lazy heap of up to $E$ entries no longer fits in the CPU cache. C++ solves 1000 airports in about 0.12 s. (The C++ program uses its own random generator, so its instances differ from the Python ones but have the same size and weight model.)

---

## 9. Technology Stack

- **Language:** Python 3 (heapq, math, random, csv) and C++17 (priority_queue, chrono)
- **Visualisation:** Matplotlib, NumPy
- **Verification:** NetworkX (independent Kruskal MST)
- **Version control:** Git and GitHub

---

## 10. Project Structure

```
air-traffic-control/
├── prim_atc.py              # Weight model, Prim's algorithm, baselines, delay/fuel simulation
├── prim_atc.cpp             # C++17 implementation with timing
├── visualize.py             # Route map, sector occupancy, traffic flow, workflow chart
├── analysis.py              # Scalability and baseline comparison experiments
├── data/
│   └── sample_airports.csv  # Sample data set of 12 airports
├── results/                 # Generated graphs (*.png) and scalability.csv
├── requirements.txt         # Python dependencies
└── README.md                # Documentation
```

---

## 11. Testing and Verification

- **Correctness:** for 12, 50, 200 and 400 airports the total weight of `prim_mst` equals the MST weight computed by NetworkX (Kruskal) to six decimal places, and the output is a tree with exactly $V-1$ edges.
- **Reproducibility:** all random data use fixed seeds, so every figure and table can be regenerated.
- **Performance:** run time averaged over 3 runs for 10, 25, 50, 100, 200, 400, 600, 800 and 1000 airports.

---

## 12. Installation and Execution

```bash
# 1. Clone the repository
git clone https://github.com/nks98287962-ship-it/air-traffic-control.git
cd air-traffic-control

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the MST for the 12 sample airports
python prim_atc.py

# 4. Generate visualisations -> results/
python visualize.py

# 5. Run the scalability and comparison analysis -> results/
python analysis.py

# 6. C++ version (optional argument = number of airports)
g++ -O2 -std=c++17 -o prim_atc prim_atc.cpp
./prim_atc 1000
```

---

## 13. Limitations and Future Scope

**Limitations**

- Airports, capacities and congestion are synthetic; delay, fuel and utilisation come from an assumed model.
- A spanning tree has no redundant paths, so it models the backbone of the network only.
- Aircraft trajectories, collision avoidance, weather and time-varying congestion are not simulated.
- The weight function trades some distance for lower congestion, so the tree is longer than a distance-only MST.

**Future scope**

- Use real airport and traffic data and validate against a professional simulator (for example the EUROCONTROL tools).
- Compare the lazy binary heap with the $O(V^2)$ array version and Fibonacci heap; compare with Kruskal and shortest-path routing.
- Add redundant links for fault tolerance and make congestion time-dependent.
- Port the implementation to C and Java.

---

## Student Information

- **Student Name:** Neeraj Sharma
- **UID:** 26MCI10177
- **Course:** MCA (AI & ML)
- **University:** Chandigarh University
- **Subject:** Design and Analysis of Algorithms (DAA)

## Project Repository

https://github.com/nks98287962-ship-it/air-traffic-control
