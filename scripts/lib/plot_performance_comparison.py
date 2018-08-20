#!/usr/bin/env python

# Benchmark hole-ice code performance.
# https://github.com/fiedl/hole-ice-study/issues/49

benchmarks = [
  {"name": "baseline", "user": [9.87, 9.88, 9.95, 9.99, 10.12, 10.01, 10.58, 10.51, 10.13, 9.98], "system": [7.69, 7.43, 7.23, 7.73, 7.50, 7.24, 10.16, 7.95, 7.89, 7.74]},
  {"name": "standard clsim", "user": [18.67, 19.59, 19.58], "system": [8.41, 8.72, 8.51]},
  {"name": "hole-ice code 2017\nhole ice factor 1", "user": [17.87, 18.25, 18.58], "system": [8.06, 8.51, 8.65]},
  {"name": "hole-ice code 2017\nwith strong hole ice", "user": [21.31, 22.29, 23.01], "system": [8.64, 8.72, 9.03]},
  {"name": "hole-ice code 2018\nwith layers, moderate hole ice", "user": [18.39, 18.81, 19.34], "system": [8.44, 8.59, 8.69]},
  {"name": "hole-ice code 2018\nwithout layers, without hole ice", "user": [18.28, 19.05, 18.93], "system": [8.56, 9.02, 8.83]},
  {"name": "hole-ice code 2018\nwith layers, with strong hole ice", "user": [22.15, 23.01, 22.65], "system": [8.57, 8.51, 8.69]},
  {"name": "hole-ice code 2018\nwithout layers, moderate hole ice", "user": [19.14, 19.72, 19.02], "system": [8.55, 9.00, 8.66]},
  {"name": "hole-ice code 2018\nwith layers, no hole ice", "user": [18.42, 18.26, 19.53], "system": [8.29, 8.55, 8.76]}
]

import numpy as np

for benchmark in benchmarks:
  benchmark["user_mean"] = np.mean(benchmark["user"])
  benchmark["user_error"] = np.std(benchmark["user"])
  benchmark["system_mean"] = np.mean(benchmark["system"])
  benchmark["system_error"] = np.std(benchmark["system"])
  benchmark["sum"] = [x + y for x, y in zip(benchmark["user"], benchmark["system"])]
  benchmark["sum_mean"] = np.mean(benchmark["sum"])
  benchmark["sum_error"] = np.std(benchmark["sum"])

baseline = benchmarks[0]
benchmarks.pop(0)

for benchmark in benchmarks:
  benchmark["sum_minus_baseline_mean"] = benchmark["sum_mean"] - baseline["sum_mean"]
  benchmark["sum_minus_baseline_error"] = benchmark["sum_error"] + baseline["sum_error"]

benchmarks = sorted(benchmarks, key=lambda k: k["sum_minus_baseline_mean"], reverse=True)

# https://matplotlib.org/gallery/lines_bars_and_markers/barh.html
import matplotlib.pyplot as plt

plt.rcdefaults()
fig, ax = plt.subplots(facecolor='white')

names = list(benchmark["name"] for benchmark in benchmarks)
y_pos = np.arange(len(benchmarks))
means = list(benchmark["sum_minus_baseline_mean"] for benchmark in benchmarks)
errors = list(benchmark["sum_minus_baseline_error"] for benchmark in benchmarks)

ax.barh(y_pos, means, xerr=errors, align='center', color='green', ecolor='black')
ax.set_yticks(y_pos)
ax.set_yticklabels(names)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_aspect(1)
ax.set_xlabel('Propagation time (usr+sys) [s]')
ax.set_title('Performance comparison: Propagating 1e5 photons')

plt.show()

