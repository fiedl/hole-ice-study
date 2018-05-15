#!/usr/bin/env python

# See: https://github.com/fiedl/hole-ice-study/issues/66

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

import sys
import pandas

data_file = "~/hole-ice-study/results/cross_checks/cross_check_66.txt"
#data_file = "~/hole-ice-study/scripts/FiringRange/tmp/cross_check.txt"
data = pandas.read_csv(data_file, delim_whitespace = True, names = ["cross", "check", "key", "equals", "photonTotalPathLength"])

import numpy as np
import matplotlib.pyplot as plt

# prepare canvas
fig, axes = plt.subplots(1, 2, facecolor="white")

range_min = 0.0
boundary1 = 1.0
boundary2 = 2.0
range_max = 5.0
plot_range = (range_min, range_max)
num_of_bins = 50

def three_exponentials(x, first_n0, second_n0, third_n0, first_inverse_lambda, second_inverse_lambda, third_inverse_lambda):
  global boundary1, boundary2
  return np.piecewise(x, \
      [x < boundary1 - 0.05, (x > boundary1 + 0.05) & (x < boundary2 - 0.05), x > boundary2 + 0.05], \
      [lambda x: first_n0 * np.exp(-x * first_inverse_lambda), lambda x: second_n0 * np.exp(-(x - boundary1) * second_inverse_lambda), lambda x: third_n0 * np.exp(-(x - boundary2) * third_inverse_lambda)])

for ax in axes:

  # histogram the data
  n, bins, patches = ax.hist(data["photonTotalPathLength"], bins = num_of_bins, range = plot_range, label = 'simulation data, $\lambda_{\mathrm{abs},1}$ = 1.0m, $\lambda_{\mathrm{abs},2}$ = 0.1m')
  bin_width = (range_max - range_min) / num_of_bins
  x = bins[0:-1] + bin_width / 2

  # fit
  from scipy.optimize import curve_fit
  parameters, cov = curve_fit(three_exponentials, x, n)

  print parameters
  first_lambda = 1.0 / parameters[3]
  second_lambda = 1.0 / parameters[4]
  third_lambda = 1.0 / parameters[5]

  # plot fit piecewise
  x = np.linspace(0.0, boundary1 - 0.05, 25)
  y = parameters[0] * np.exp(-x / first_lambda)
  ax.plot(x, y, label = 'exponential fit, $\lambda_{\mathrm{abs},1}$ = ' + str(round(first_lambda, 3)) + 'm', linewidth = 2.0)

  x = np.linspace(boundary1 + 0.05, boundary2 - 0.05, 25)
  y = parameters[1] * np.exp(-(x - boundary1) / second_lambda)
  ax.plot(x, y, label = 'exponential fit, $\lambda_{\mathrm{abs},2}$ = ' + str(round(second_lambda, 3)) + 'm', linewidth = 2.0)

  x = np.linspace(boundary2, range_max, 25)
  y = parameters[2] * np.exp(-(x - boundary2) / third_lambda)
  ax.plot(x, y, label = 'exponential fit, $\lambda_{\mathrm{abs},3}$ = ' + str(round(third_lambda, 3)) + 'm', linewidth = 2.0)


  ax.set_xlabel("photon total path length [m]")

  ax.grid()
  ax.legend(loc = "upper right")

axes[1].set_yscale("log")

number_of_photons = data["photonTotalPathLength"].count()
fig.suptitle("Cross check #66: Photons within hole ice, number of photons = " + str(number_of_photons), fontsize = 14)

plt.show()