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

true_first_lambda = 1.0
true_second_lambda = 0.75
true_third_lambda = 1.0

range_min = 0.0
boundary1 = 1.0
boundary2 = 2.0
range_max = 5.0
plot_range = (range_min, range_max)
num_of_bins = 60

def three_exponentials(x, first_n0, second_n0, third_n0, first_lambda, second_lambda, third_lambda):
  global boundary1, boundary2
  return np.piecewise(x, \
      [x < boundary1 - 0.05, (x > boundary1 + 0.05) & (x < boundary2 - 0.05), x > boundary2 + 0.05], \
      [lambda x: first_n0 * np.exp(-x * 1.0 / first_lambda), lambda x: second_n0 * np.exp(-(x - boundary1) * 1.0 / second_lambda), lambda x: third_n0 * np.exp(-(x - boundary2) * 1.0 / third_lambda)])

def str_round(number):
  return "{:.4f}".format(number)

for ax in axes:

  # histogram the data
  n, bins, patches = ax.hist(data["photonTotalPathLength"], bins = num_of_bins, range = plot_range, label = 'simulation data, $\lambda_{\mathrm{abs},1,3}$ = ' + str_round(true_first_lambda) + 'm, $\lambda_{\mathrm{abs},2}$ = ' + str_round(true_second_lambda) + 'm')
  bin_width = (range_max - range_min) / num_of_bins
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
  parameters, cov = curve_fit(three_exponentials, x, n,
      bounds = [[0, 0, 0, 0, 0, 0], [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf]],
      sigma = n_error)

  first_lambda = parameters[3]
  second_lambda = parameters[4]
  third_lambda = parameters[5]

  errors = np.sqrt(np.diag(cov))
  first_lambda_error = errors[3]
  second_lambda_error = errors[4]
  third_lambda_error = errors[5]

  print parameters
  print errors

  # plot fit piecewise
  x = np.linspace(0.0, boundary1 - 0.05, 25)
  y = parameters[0] * np.exp(-x / first_lambda)
  ax.plot(x, y, label = 'exponential fit, $\lambda_{\mathrm{abs},1}$ = ' + str_round(first_lambda) + 'm $\pm$ ' + str_round(first_lambda_error) + 'm', linewidth = 2.0)

  x = np.linspace(boundary1 + 0.05, boundary2 - 0.05, 25)
  y = parameters[1] * np.exp(-(x - boundary1) / second_lambda)
  ax.plot(x, y, label = 'exponential fit, $\lambda_{\mathrm{abs},2}$ = ' + str_round(second_lambda) + 'm $\pm$ ' + str_round(second_lambda_error) + 'm', linewidth = 2.0)

  x = np.linspace(boundary2, range_max, 25)
  y = parameters[2] * np.exp(-(x - boundary2) / third_lambda)
  ax.plot(x, y, label = 'exponential fit, $\lambda_{\mathrm{abs},3}$ = ' + str_round(third_lambda) + 'm $\pm$ ' + str_round(third_lambda_error) + 'm', linewidth = 2.0)


  ax.set_xlabel("photon total path length [m]")

  ax.grid()
  ax.legend(loc = "upper right")

axes[1].set_yscale("log")

number_of_photons = data["photonTotalPathLength"].count()
fig.suptitle("Cross check #66: Photons passing through hole ice, number of photons = " + str(number_of_photons), fontsize = 14)

plt.show()