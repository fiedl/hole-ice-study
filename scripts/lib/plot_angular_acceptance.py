#!/usr/bin/env python

# Usage:
# python plot_angular_acceptance.py ~/hole-ice-study/results/angular_acceptance_ice_paper

import sys
import pandas
import json

data_root_folder = sys.argv[1]

import os
import glob2

options_files = glob2.glob(os.path.join(data_root_folder, "./**/options.txt"))
data_dirs = list((os.path.dirname(options_file) for options_file in options_files))

import matplotlib as mpl
from matplotlib.mlab import griddata
from matplotlib import ticker
import matplotlib.pyplot as plt

import scipy.special
import numpy as np

def reference_curve(angle):
  x = np.cos(2 * np.pi * angle / 360.0)
  a = 0.32813; b = 0.63899; c = 0.20049; d =-1.2250; e =-0.14470; f = 4.1695;
  g = 0.76898; h =-5.8690; i =-2.0939; j = 2.3834; k = 1.0435;
  return a + b*x + c*x**2 + d*x**3 + e*x**4 + f*x**5 + g*x**6 + h*x**7 + i*x**8 + j*x**9 + k*x**10

def str_round(number):
  return "{:.4f}".format(number)


# prepare canvas
fig, ax = plt.subplots(1, 1, facecolor="white")

# Plot reference curve
reference_curve_angles = np.arange(0.0, 180.0, 0.1)
ax.plot(np.cos(reference_curve_angles * 2 * np.pi / 360.0), reference_curve(reference_curve_angles), label = "DOM angular acceptance with hole-ice approximation", linewidth = 2)

for data_dir in data_dirs:
  data_files = glob2.glob(os.path.join(data_dir, "./angle_hits_and_photons_*.txt"))
  data_rows = (pandas.read_csv(data_file, delim_whitespace = True, names = ["angle", "hits", "photons"]) for data_file in data_files)
  data = pandas.concat(data_rows, ignore_index = True)

  options_file = os.path.join(data_dir, "./options.json")
  simulation_options = json.load(open(options_file))

  # Calculate the ln_likelihood, i.e. the probability of data matching the
  # reference curve at all angles.
  #
  # See: https://github.com/fiedl/hole-ice-study/issues/12#issuecomment-376179961
  #
  angles = data["angle"].unique()
  ln_likelihood_summands = [0] * len(angles)

  # Gauge factor
  #
  # See: https://github.com/fiedl/hole-ice-study/issues/12#issuecomment-376580354
  #
  p_0 = 0.0039667 # plane waves
  #p_0 = 0.045007900000000003 # pencil beam

  sensitivity = []
  sensitivity_error = []

  for i, angle in enumerate(angles):
    n = data[data.angle == angle]["photons"].sum()
    k_i = data[data.angle == angle]["hits"].sum()
    p_i = reference_curve(angle) * p_0

    ln_binomial_coefficient = \
        scipy.special.gammaln(n + 1) - scipy.special.gammaln(k_i + 1) - scipy.special.gammaln(n - k_i + 1)

    ln_likelihood_summands[i] = \
        ln_binomial_coefficient + k_i * np.log(p_i) + (n - k_i) * np.log(1 - p_i)

    sensitivity.append(k_i / n / p_0)
    # sensitivity_error.append(np.sqrt(n * p_0 * (k_i / n) * (1 - (k_i / n)))) # Bernoulli, Leo, S. 85
    # sensitivity_error.append(np.sqrt(k_i * p_0)) # Poisson, 2018-07-10, Leo, S. 98

    # Finding the error numerically, 2018-03-15, 2018-07-10
    min_neg_ln_likelihood = np.inf
    for p in np.arange(0.01, 0.99, 0.01) * p_0:
      ln_lh = ln_binomial_coefficient + k_i * np.log(p) + (n - k_i) * np.log(1 - p)
      # min_neg_ln_likelihood = np.min([min_neg_ln_likelihood, -ln_lh])
      if -ln_lh < min_neg_ln_likelihood:
        min_neg_ln_likelihood = -ln_lh
        best_p = p

    left_p = np.nan
    for p in np.arange(best_p / p_0, 0.01, -0.01) * p_0:
      ln_lh = ln_binomial_coefficient + k_i * np.log(p) + (n - k_i) * np.log(1 - p)
      if -ln_lh > min_neg_ln_likelihood + 0.5:
        left_p = p
        break

    right_p = np.nan
    for p in np.arange(best_p / p_0, 0.99, 0.01) * p_0:
      ln_lh = ln_binomial_coefficient + k_i * np.log(p) + (n - k_i) * np.log(1 - p)
      if -ln_lh > min_neg_ln_likelihood + 0.5:
        right_p = p
        break

    error = right_p - left_p
    sensitivity_error.append(error / p_0)


  ln_likelihood = sum(ln_likelihood_summands)


  # Plot simulation data points
  ax.errorbar(np.cos(angles * 2 * np.pi / 360.0), sensitivity, fmt = "-o", yerr = sensitivity_error, label = "hole-ice simulation, $\lambda_\mathrm{e}$=" + str_round(simulation_options["hole_ice_effective_scattering_length"]) + "m, $r$=" + str_round(simulation_options["hole_ice_radius"]) + "m, LLH = " + str(ln_likelihood))

  ax.set(xlabel = "cos(eta)")
  ax.set(ylabel = "relative sensitivity")

  ax.legend(loc = "best")
  ax.grid()

ax.set_title("Angular acceptance")

plt.show()