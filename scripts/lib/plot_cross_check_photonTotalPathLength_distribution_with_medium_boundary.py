#!/usr/bin/env python

# See: https://github.com/fiedl/hole-ice-study/issues/65

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

import sys
import pandas

data_file = "~/hole-ice-study/results/cross_checks/cross_check_65.txt"
#data_file = "~/hole-ice-study/scripts/FiringRange/tmp/cross_check.txt"
data = pandas.read_csv(data_file, delim_whitespace = True, names = ["cross", "check", "key", "equals", "photonTotalPathLength"])

import numpy as np
import matplotlib.pyplot as plt

# prepare canvas
fig, axes = plt.subplots(1, 2, facecolor="white")

plot_range_min = 0.0
plot_range_border = 1.0
plot_range_max = 2.2
plot_range = (plot_range_min, plot_range_max)

def two_exponentials(x, first_n0, second_n0, first_inverse_lambda, second_inverse_lambda, plot_range_border):
  #global plot_range_border
  return np.piecewise(x, \
      [x < plot_range_border - 0.05, x >= plot_range_border + 0.05], \
      [lambda x: first_n0 * np.exp(-x * first_inverse_lambda), lambda x: second_n0 * np.exp(-(x - plot_range_border) * second_inverse_lambda)])

def exponential(x, n0, lambd):
  return n0 * np.exp(-lambd * (x - 1.0))

for ax in axes:

  # histogram the data
  n, bins, patches = ax.hist(data["photonTotalPathLength"], bins = 50, range = plot_range, label = 'simulation data, $\lambda_{\mathrm{abs},1}$ = 1.0m, $\lambda_{\mathrm{abs},2}$ = 0.1m')
  bin_width = (plot_range_max - plot_range_min) / 50
  x = bins[0:-1] + bin_width / 2

  # fit
  from scipy.optimize import curve_fit
  parameters, cov = curve_fit(two_exponentials, x, n,
      bounds = [[0, 0, 0, 0, plot_range_min], [np.inf, np.inf, np.inf, np.inf, plot_range_max]])

  print parameters
  first_lambda = 1.0 / parameters[2]
  second_lambda = 1.0 / parameters[3]

  # plot fit piecewise
  x = np.linspace(0.0, 0.95, 25)
  y = parameters[0] * np.exp(-x / first_lambda)
  ax.plot(x, y, label = 'exponential fit, $\lambda_{\mathrm{abs},1}$ = ' + str(round(first_lambda, 3)) + 'm', linewidth = 2.0)

  x = np.linspace(1.05, 2.2, 25)
  y = parameters[1] * np.exp(-(x - plot_range_border) / second_lambda)
  ax.plot(x, y, label = 'exponential fit, $\lambda_{\mathrm{abs},2}$ = ' + str(round(second_lambda, 3)) + 'm', linewidth = 2.0)


  ax.set_xlabel("photon total path length [m]")

  ax.grid()
  ax.legend(loc = "upper right")

axes[1].set_yscale("log")

number_of_photons = data["photonTotalPathLength"].count()
fig.suptitle("Cross check #65: Photons within hole ice, number of photons = " + str(number_of_photons), fontsize = 14)

plt.show()