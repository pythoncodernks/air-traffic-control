"""Air Traffic Control - route optimisation using Prim's Minimum Spanning Tree.

Edge weight combines distance, airport capacity and airspace congestion:
    w(u,v) = distance(u,v) * (1 + congestion(u,v)) / sqrt(cap(u) * cap(v)) * K
Lower weight = a better (shorter, less congested, higher capacity) corridor.
"""
import heapq, math, random, time

K = 10.0  # scaling constant so weights stay readable


class Airport:
    def __init__(self, code, x, y, capacity):
        self.code, self.x, self.y, self.capacity = code, x, y, capacity


def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def edge_weight(a, b, congestion=0.0):
    return K * distance(a, b) * (1.0 + congestion) / math.sqrt(a.capacity * b.capacity)


def generate_airports(n, seed=42, area=2000):
    rnd = random.Random(seed)
    return [Airport(f"AP{i:03d}", rnd.uniform(0, area), rnd.uniform(0, area),
                    rnd.choice([20, 30, 40, 60, 80, 100])) for i in range(n)]


def generate_congestion(n, seed=7):
    rnd = random.Random(seed)
    return {(i, j): rnd.uniform(0, 0.5) for i in range(n) for j in range(i + 1, n)}


def prim_mst(airports, congestion=None, start=0):
    """Prim's algorithm with a binary min-heap on a complete graph.
    Returns (edges, total_weight). Time O(E log V), E = V(V-1)/2."""
    n = len(airports)
    congestion = congestion or {}
    visited = [False] * n
    edges, total = [], 0.0
    heap = [(0.0, start, -1)]
    while heap and len(edges) < n - 1 + 1:
        w, u, parent = heapq.heappop(heap)
        if visited[u]:
            continue
        visited[u] = True
        if parent != -1:
            edges.append((parent, u, w))
            total += w
        for v in range(n):
            if not visited[v]:
                c = congestion.get((min(u, v), max(u, v)), 0.0)
                heapq.heappush(heap, (edge_weight(airports[u], airports[v], c), v, u))
    return edges, total


def shortest_path_tree_length(edges, airports):
    return sum(distance(airports[u], airports[v]) for u, v, _ in edges)


def delay_and_fuel(edges, airports, congestion):
    """Simulation model (assumptions, see report Sec. 3.5):
      en-route delay (min)  = distance / 800 km/h * 60 * (1 + congestion)
      airport queue (min)   = 30 * degree / capacity   (traffic through a node vs its capacity)
      fuel (kg)             = distance * 4.5 kg/km * (1 + congestion)  (holding/detours burn extra)
    Returns (distance, total_delay, fuel)."""
    deg = {}
    for u, v, _ in edges:
        deg[u] = deg.get(u, 0) + 1; deg[v] = deg.get(v, 0) + 1
    dist = delay = fuel = 0.0
    for u, v, _ in edges:
        d = distance(airports[u], airports[v]); c = congestion.get((min(u, v), max(u, v)), 0.0)
        dist += d; delay += d / 800 * 60 * (1 + c); fuel += d * 4.5 * (1 + c)
    delay += sum(30 * k / airports[i].capacity for i, k in deg.items())
    return dist, delay, fuel


def star_tree(airports):
    """Baseline: every airport connected to the single highest-capacity hub."""
    hub = max(range(len(airports)), key=lambda i: airports[i].capacity)
    return [(hub, v, 0.0) for v in range(len(airports)) if v != hub]


def random_tree(airports, seed=0):
    """Baseline: random spanning tree (each new airport attaches to a random earlier one)."""
    rnd = random.Random(seed)
    order = list(range(len(airports))); rnd.shuffle(order)
    return [(rnd.choice(order[:k]), order[k], 0.0) for k in range(1, len(order))]


def distance_only_mst(airports):
    """Baseline: plain distance MST that ignores capacity and congestion."""
    n = len(airports)
    visited, edges, heap = [False] * n, [], [(0.0, 0, -1)]
    while heap:
        w, u, p = heapq.heappop(heap)
        if visited[u]:
            continue
        visited[u] = True
        if p != -1:
            edges.append((p, u, w))
        for v in range(n):
            if not visited[v]:
                heapq.heappush(heap, (distance(airports[u], airports[v]), v, u))
    return edges


if __name__ == "__main__":
    ap = generate_airports(12)
    cg = generate_congestion(12)
    t = time.perf_counter()
    mst, total = prim_mst(ap, cg)
    print(f"MST edges: {len(mst)}  total weight: {total:.2f}  time: {(time.perf_counter()-t)*1000:.3f} ms")
    for u, v, w in mst:
        print(f"{ap[u].code} -- {ap[v].code}  dist={distance(ap[u], ap[v]):7.1f} km  weight={w:7.2f}")
