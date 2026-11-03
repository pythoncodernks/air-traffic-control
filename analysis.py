"""Performance + scalability analysis. Run: python analysis.py  -> results/*.csv, results/*.png"""
import csv, time, math, statistics
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from prim_atc import *

SIZES = [10, 25, 50, 100, 200, 400, 600, 800, 1000]
METHODS = ["prim", "dist_mst", "random", "star"]
rows = []

def cong_mean(es, cg):
    return statistics.mean(cg[(min(u, v), max(u, v))] for u, v, _ in es)

def max_load(es, ap):                      # worst airport utilisation = degree / capacity
    deg = {}
    for u, v, _ in es: deg[u] = deg.get(u, 0) + 1; deg[v] = deg.get(v, 0) + 1
    return max(k / ap[i].capacity for i, k in deg.items())

for n in SIZES:
    ap, cg = generate_airports(n), generate_congestion(n)
    times = []
    for _ in range(3):
        t = time.perf_counter(); edges, tot = prim_mst(ap, cg); times.append((time.perf_counter() - t) * 1000)
    nets = {"prim": edges, "dist_mst": distance_only_mst(ap), "star": star_tree(ap)}
    rnd = [random_tree(ap, s) for s in range(5)]
    row = dict(n=n, edges_mst=len(edges), edges_graph=n * (n - 1) // 2, time_ms=round(statistics.mean(times), 3))
    for m, es in nets.items():
        d, dl, f = delay_and_fuel(es, ap, cg)
        row.update({f"dist_{m}": round(d), f"delay_{m}": round(dl), f"fuel_{m}": round(f),
                    f"cong_{m}": round(cong_mean(es, cg), 3), f"load_{m}": round(max_load(es, ap), 3)})
    rs = [delay_and_fuel(es, ap, cg) for es in rnd]
    row.update(dist_random=round(statistics.mean(r[0] for r in rs)), delay_random=round(statistics.mean(r[1] for r in rs)),
               fuel_random=round(statistics.mean(r[2] for r in rs)),
               cong_random=round(statistics.mean(cong_mean(es, cg) for es in rnd), 3),
               load_random=round(statistics.mean(max_load(es, ap) for es in rnd), 3))
    rows.append(row); print(n, row["time_ms"], row["delay_prim"], row["delay_dist_mst"], row["delay_random"], row["delay_star"])

with open("results/scalability.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
ns = [r["n"] for r in rows]

plt.figure(figsize=(6.4, 4)); plt.plot(ns, [r["time_ms"] for r in rows], "o-", color="#1f4e8c")
plt.xlabel("Number of airports (V)"); plt.ylabel("Runtime (ms)"); plt.title("Prim's runtime vs number of airports"); plt.grid(alpha=.3)
plt.tight_layout(); plt.savefig("results/runtime.png", dpi=170); plt.close()

plt.figure(figsize=(6.4, 4))
norm = [r["time_ms"] / (r["edges_graph"] * math.log2(r["n"])) * 1e3 for r in rows]
plt.plot(ns, norm, "s-", color="#b03a2e"); plt.xlabel("Number of airports (V)")
plt.ylabel("time / (E log V)  [microsec per unit]"); plt.title("Normalised cost (flat curve = O(E log V))"); plt.grid(alpha=.3)
plt.tight_layout(); plt.savefig("results/complexity.png", dpi=170); plt.close()

sty = {"prim": ("Proposed Prim ATC", "o-", "#1f4e8c"), "dist_mst": ("Distance-only MST", "s--", "#7f8c8d"),
       "random": ("Random tree", "^:", "#e67e22"), "star": ("Single-hub star", "v-.", "#b03a2e")}
fig, ax = plt.subplots(1, 3, figsize=(11, 3.7))
for a, (k, t) in zip(ax, [("delay", "Total delay (min)"), ("fuel", "Total fuel (kg)"), ("load", "Max airport utilisation")]):
    for m in METHODS:
        lab, st, col = sty[m]; a.plot(ns, [r[f"{k}_{m}"] for r in rows], st, color=col, label=lab, ms=4)
    a.set_title(t, fontsize=10); a.set_xlabel("Airports"); a.grid(alpha=.3)
    if k == "load": a.set_yscale("log")
ax[0].legend(fontsize=7); plt.tight_layout(); plt.savefig("results/comparison.png", dpi=170); plt.close()
