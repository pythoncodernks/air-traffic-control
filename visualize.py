"""Visualisation tools: MST route map, sector occupancy heat-map, traffic-flow map, workflow chart.
Run: python visualize.py  -> results/*.png"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
from prim_atc import *

N, AREA, GRID = 25, 2000, 4
ap, cg = generate_airports(N), generate_congestion(N)
edges, total = prim_mst(ap, cg)
base = distance_only_mst(ap)
COL = {20: "#e74c3c", 30: "#e67e22", 40: "#f1c40f", 60: "#2ecc71", 80: "#3498db", 100: "#8e44ad"}

def draw_airports(ax, labels=True):
    for a in ap:
        ax.scatter(a.x, a.y, s=a.capacity * 3 + 25, c=COL[a.capacity], edgecolors="k", zorder=3)
        if labels: ax.annotate(a.code[2:], (a.x, a.y), fontsize=6, ha="center", va="center", zorder=4)
    ax.set_xlim(-80, AREA + 80); ax.set_ylim(-80, AREA + 80); ax.set_aspect("equal")
    ax.set_xlabel("x (km)"); ax.set_ylabel("y (km)")

# 1. network of candidate routes vs MST routes
fig, ax = plt.subplots(1, 2, figsize=(11, 5.2))
for i in range(N):
    for j in range(i + 1, N):
        ax[0].plot([ap[i].x, ap[j].x], [ap[i].y, ap[j].y], c="#bbb", lw=.3, zorder=1)
draw_airports(ax[0]); ax[0].set_title(f"Complete graph: {N*(N-1)//2} candidate corridors", fontsize=10)
for u, v, w in edges:
    c = cg[(min(u, v), max(u, v))]
    ax[1].plot([ap[u].x, ap[v].x], [ap[u].y, ap[v].y], c=plt.cm.RdYlGn_r(c / .5), lw=2.2, zorder=2)
draw_airports(ax[1]); ax[1].set_title(f"Prim MST: {len(edges)} corridors (colour = congestion)", fontsize=10)
from matplotlib.lines import Line2D
ax[0].legend(handles=[Line2D([], [], marker="o", ls="", mfc=c, mec="k", label=f"cap {k}") for k, c in COL.items()],
             fontsize=7, loc="lower left", ncol=2)
plt.tight_layout(); plt.savefig("results/mst_network.png", dpi=170); plt.close()

# 2. sector occupancy: airports + corridor length per 4x4 sector
occ = np.zeros((GRID, GRID)); cap = np.zeros((GRID, GRID)); step = AREA / GRID
for a in ap:
    r, c = min(int(a.y // step), GRID - 1), min(int(a.x // step), GRID - 1); cap[r, c] += a.capacity
def sector_load(es):
    L = np.zeros((GRID, GRID))
    for u, v, _ in es:
        for t in np.linspace(0, 1, 60):
            x = ap[u].x + t * (ap[v].x - ap[u].x); y = ap[u].y + t * (ap[v].y - ap[u].y)
            L[min(int(y // step), GRID - 1), min(int(x // step), GRID - 1)] += distance(ap[u], ap[v]) / 60
    return L
fig, ax = plt.subplots(1, 2, figsize=(10, 4.4)); vmax = max(sector_load(edges).max(), sector_load(base).max())
for a_, es, t in [(ax[0], base, "Distance-only MST"), (ax[1], edges, "Proposed Prim ATC")]:
    L = sector_load(es); im = a_.imshow(L, origin="lower", cmap="YlOrRd", vmin=0, vmax=vmax, extent=[0, AREA, 0, AREA])
    for r in range(GRID):
        for c in range(GRID): a_.text((c + .5) * step, (r + .5) * step, f"{L[r, c]:.0f}", ha="center", va="center", fontsize=8)
    a_.set_title(f"{t}\nroute-km per sector", fontsize=10)
fig.colorbar(im, ax=ax, shrink=.8, label="route-km in sector"); plt.savefig("results/sector_occupancy.png", dpi=170, bbox_inches="tight"); plt.close()

# 3. traffic flow: subtree sizes = number of airports served through each corridor (hub = root)
adj = {i: [] for i in range(N)}
for u, v, _ in edges: adj[u].append(v); adj[v].append(u)
size = {}
def dfs(u, p):
    size[u] = 1
    for v in adj[u]:
        if v != p: dfs(v, u); size[u] += size[v]
dfs(0, -1)
fig, ax = plt.subplots(figsize=(6.4, 6))
for u, v, _ in edges:
    child = v if size.get(v, 0) < size.get(u, 0) else u
    ax.plot([ap[u].x, ap[v].x], [ap[u].y, ap[v].y], c="#1f4e8c", lw=1 + 0.6 * size[child], alpha=.75, zorder=2)
draw_airports(ax); ax.set_title("Traffic-flow pattern: line width = airports served through the corridor", fontsize=9)
plt.tight_layout(); plt.savefig("results/traffic_flow.png", dpi=170); plt.close()

# 4. workflow figure
fig, ax = plt.subplots(figsize=(4.6, 6.4)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 14)
steps = ["Input: airports (x, y, capacity)\n+ airspace congestion", "Build complete graph\nw(u,v) = K·d·(1+c) / sqrt(cap_u·cap_v)",
         "Prim's algorithm\n(min-heap from start airport)", "Minimum spanning tree\n(V-1 corridors)",
         "Simulation: delay, fuel,\ncongestion, airport load", "Visualisation: routes,\nsectors, traffic flow"]
for i, s in enumerate(steps):
    y = 12.2 - i * 2.35
    ax.add_patch(FancyBboxPatch((0.8, y), 8.4, 1.5, boxstyle="round,pad=0.05", fc="#dbe7f7" if i % 2 == 0 else "#e8f5e9", ec="#1f4e8c"))
    ax.text(5, y + .75, s, ha="center", va="center", fontsize=8.5)
    if i < len(steps) - 1: ax.annotate("", (5, y - .85), (5, y), arrowprops=dict(arrowstyle="-|>", color="#333"))
plt.savefig("results/workflow.png", dpi=170, bbox_inches="tight"); plt.close()
print("figures saved; MST total weight", round(total, 2))
