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

true_first_lambda = 1.0
true_second_lambda = 0.1

plot_range_min = 0.0
plot_range_border = 1.0
plot_range_max = 2.2
plot_range = (plot_range_min, plot_range_max)

def two_exponentials(x, first_n0, second_n0, first_lambda, second_lambda):
  global plot_range_border
  return np.piecewise(x, \
      [x < 0.95, x >= 1.05], \
      [lambda x: first_n0 * np.exp(-x * 1.0 / first_lambda), lambda x: second_n0 * np.exp(-(x - plot_range_border) * 1.0 / second_lambda)])

def str_round(number):
  return "{:.4f}".format(number)

for ax in axes:

  # histogram the data
  n, bins, patches = ax.hist(data["photonTotalPathLength"], bins = 50, range = plot_range, label = 'simulation data, $\lambda_{\mathrm{abs},1}$ = ' + str_round(true_first_lambda) + 'm, $\lambda_{\mathrm{abs},2}$ = ' + str_round(true_second_lambda) + 'm')
  bin_width = (plot_range_max - plot_range_min) / 50
  x = bins[0:-1] + bin_width / 2
  n_error = np.sqrt(n)

  # filter for inf values: `ValueError: Residuals are not finite in the initial point.`
  # https://stackoverflow.com/a/33876974/2066546
  valid = ~(n == 0)
  n = n[valid]
  x = x[valid]
  n_error = n_error[valid]

  # fit
  from scipy.optimize import curve_fit
  parameters, cov = curve_fit(two_exponentials, x, n,
      bounds = [[0, 0, 0, 0], [np.inf, np.inf, np.inf, np.inf]],
      sigma = n_error)

  first_lambda = parameters[2]
  second_lambda = parameters[3]
  errors = np.sqrt(np.diag(cov))
  first_lambd_error = errors[2]
  second_lambd_error = errors[3]

  print parameters
  print errors

  # plot fit piecewise
  x = np.linspace(0.0, 0.95, 25)
  y = parameters[0] * np.exp(-x / first_lambda)
  ax.plot(x, y, label = 'exponential fit, $\lambda_{\mathrm{abs},1}$ = ' + str_round(first_lambda) + 'm $\pm$ ' + str_round(first_lambd_error) + 'm', linewidth = 2.0)

  x = np.linspace(1.05, 2.2, 25)
  y = parameters[1] * np.exp(-(x - plot_range_border) / second_lambda)
  ax.plot(x, y, label = 'exponential fit, $\lambda_{\mathrm{abs},2}$ = ' + str_round(second_lambda) + 'm $\pm$ ' + str_round(second_lambd_error) + 'm', linewidth = 2.0)


  ax.set_xlabel("photon total path length [m]")

  ax.grid()
  ax.legend(loc = "upper right")

axes[1].set_yscale("log")

number_of_photons = data["photonTotalPathLength"].count()
fig.suptitle("Cross check #65: Photons entering hole ice, number of photons = " + str(number_of_photons), fontsize = 14)

plt.show()