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

def exponential(x, n0, lambd):
  return n0 * np.exp(-x * 1.0 / lambd)

plot_range_min = 0.0
plot_range_max = 1.0
plot_range = (plot_range_min, plot_range_max)

def str_round(number):
  return "{:.3f}".format(number)

for ax in axes:

  # histogram the data
  n, bins, patches = ax.hist(data["photonTotalPathLength"], bins = 50, range = plot_range, label = 'simulation data, $\lambda_{\mathrm{abs}}$ = 0.1m')
  bin_width = (plot_range_max - plot_range_min) / 50
  x = bins[0:-1] #+ bin_width / 2
  n_error = np.sqrt(n)

  # filter for inf values: `ValueError: Residuals are not finite in the initial point.`
  # https://stackoverflow.com/a/33876974/2066546
  valid = ~(n == 0)
  n = n[valid]
  x = x[valid]
  n_error = n_error[valid]

  # fit
  from scipy.optimize import curve_fit
  parameters, cov = curve_fit(exponential, x, n,
      bounds = [[0, 0], [np.inf, np.inf]],
      sigma = n_error)

  fit_n0 = parameters[0]
  fit_lambd = parameters[1]
  errors = np.sqrt(np.diag(cov))
  fit_lambd_error = errors[1]

  # plot fit
  x = np.linspace(plot_range_min, plot_range_max, 50)
  y = exponential(x, fit_n0, fit_lambd)
  bin_width = (plot_range_max - plot_range_min) / 50
  ax.plot(x + bin_width / 2, y, label = 'exponential fit, $\lambda_{\mathrm{abs}}$ = ' + str_round(fit_lambd) + 'm $\pm$ ' + str_round(fit_lambd_error) + 'm', linewidth = 2.0)

  ax.set_xlabel("photon total path length [m]")

  ax.grid()
  ax.legend(loc = "upper right")

axes[1].set_yscale("log")

number_of_photons = data["photonTotalPathLength"].count()
fig.suptitle("Cross check #64: Photons within hole ice, number of photons = " + str(number_of_photons), fontsize = 14)

plt.show()