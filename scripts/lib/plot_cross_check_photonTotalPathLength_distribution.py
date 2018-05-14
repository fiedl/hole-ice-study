#!/usr/bin/env python

# See: https://github.com/fiedl/hole-ice-study/issues/64

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

import sys
import pandas

data_file = "~/hole-ice-study/results/cross_checks/cross_check_64.txt"
data = pandas.read_csv(data_file, delim_whitespace = True, names = ["cross", "check", "key", "equals", "photonTotalPathLength"])

import numpy as np
import matplotlib.pyplot as plt

# prepare canvas
fig, axes = plt.subplots(1, 2, facecolor="white")

for ax in axes:

  # histogram the data
  n, bins, patches = ax.hist(data["photonTotalPathLength"], bins = 50, label = 'simulation data, $\lambda_{\mathrm{abs}}$ = 0.1m')

  ## fit the exponential distribution
  import scipy.stats as ss
  fit_params = ss.expon.fit(data["photonTotalPathLength"])

  # plot fit
  x = np.linspace(data["photonTotalPathLength"].min(), data["photonTotalPathLength"].max(), 50)
  y = ss.expon.pdf(x, *fit_params)
  scale = 1.0 * sum(n) / sum(y)
  bin_width = (data["photonTotalPathLength"].max() - data["photonTotalPathLength"].min()) / 50
  ax.plot(x + bin_width / 2, y * scale, label = 'exponential fit, $\lambda_{\mathrm{abs}}$ = ' + str(round(fit_params[1], 3)) + 'm', linewidth = 2.0)

  ax.set_xlabel("photon total path length [m]")

  ax.grid()
  ax.legend(loc = "upper right")

axes[1].set_yscale("log")

fig.suptitle("Cross check #64: Photons within hole ice", fontsize = 14)

plt.show()