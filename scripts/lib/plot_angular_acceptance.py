#!/usr/bin/env python

# Usage:
# python plot_angular_acceptance.py ~/hole-ice-study/results/angular_acceptance_ice_paper

import argparse
parser = argparse.ArgumentParser(description = "Plot angular-acceptance curves")
parser.add_argument("data_root_folders", metavar = "FOLDER", type = str, nargs = "*")

parser.add_argument("--hole-ice", dest = "hole_ice", action='store_true')
parser.add_argument("--no-hole-ice", dest = "hole_ice", action='store_false')

parser.add_argument("--pencil-beam", dest = "pencil_beam", action = "store_true")
parser.add_argument("--plane-wave", dest = "pencil_beam", action = "store_false")

parser.add_argument("--direct-detection", dest = "direct_detection", action = "store_true")
parser.add_argument("--no-direct-detection", dest = "direct_detection", action = "store_false")

parser.add_argument("--h0-reference", dest = "h0_reference_curve", action = "store_true")
parser.add_argument("--h2-reference", dest = "h2_reference_curve", action = "store_true")
parser.add_argument("--dima-reference", dest = "dima_reference_curve", action = "store_true")

parser.add_argument("--no-log-scale", dest = "log_scale", action = "store_false")
parser.add_argument("--llh", dest = "llh", action = "store_true")

parser.set_defaults(hole_ice = True, pencil_beam = False, direct_detection = True, log_scale = True)
args = parser.parse_args()

import sys
import pandas
import json

data_root_folders = args.data_root_folders

import os
import glob2

options_files = []
for data_root_folder in data_root_folders:
  options_files += glob2.glob(os.path.join(data_root_folder, "./**/options.txt"))

data_dirs = list((os.path.dirname(options_file) for options_file in options_files))

import matplotlib as mpl
from matplotlib.mlab import griddata
from matplotlib import ticker
import matplotlib.pyplot as plt

import scipy.special
import numpy as np

def reference_curve_hole_ice(angle):
  x = np.cos(2 * np.pi * angle / 360.0)
  a = 0.32813; b = 0.63899; c = 0.20049; d =-1.2250; e =-0.14470; f = 4.1695;
  g = 0.76898; h =-5.8690; i =-2.0939; j = 2.3834; k = 1.0435;
  return a + b*x + c*x**2 + d*x**3 + e*x**4 + f*x**5 + g*x**6 + h*x**7 + i*x**8 + j*x**9 + k*x**10

def reference_curve_no_hole_ice(angle):
  x = np.cos(2 * np.pi * angle / 360.0)
  a = 0.26266; b = 0.47659; c = 0.15480; d = -0.14588; e = 0.17316; f = 1.3070;
  g = 0.44441; h = -2.3538; i = -1.3564; j = 1.2098; k = 0.81569;
  return a + b*x + c*x**2 + d*x**3 + e*x**4 + f*x**5 + g*x**6 + h*x**7 + i*x**8 + j*x**9 + k*x**10

def reference_curve_dima(angle, p):
  # https://github.com/fiedl/hole-ice-study/issues/102
  eta = 2 * np.pi * angle / 360.0
  return 0.34 * (1 + 1.5 * np.cos(eta) - np.cos(eta)**3/2) + p * np.cos(eta) * (np.cos(eta)**2 - 1)**3

def str_round(number):
  return "{:.4f}".format(number)


# prepare canvas
fig, ax = plt.subplots(1, 1, facecolor="white")

# Plot reference curve
hole_ice = args.hole_ice
if args.h0_reference_curve:
  reference_curve_angles = np.arange(0.0, 180.0, 0.1)
  label = "DOM angular acceptance"
  ax.plot(np.cos(reference_curve_angles * 2 * np.pi / 360.0), reference_curve_no_hole_ice(reference_curve_angles), label = label, linewidth = 2)
if args.h2_reference_curve:
  reference_curve_angles = np.arange(0.0, 180.0, 0.1)
  label = "A priori DOM angular acceptance with hole-ice approximation H2"
  ax.plot(np.cos(reference_curve_angles * 2 * np.pi / 360.0), reference_curve_hole_ice(reference_curve_angles), label = label, linewidth = 2)

# Plot Dima's curve if requested
if args.dima_reference_curve:
  reference_curve_angles = np.arange(0.0, 180.0, 0.1)

  # p = 0.2
  # label = "Dimas's hole-ice model, p = 0.2"
  # ax.plot(np.cos(reference_curve_angles * 2 * np.pi / 360.0), reference_curve_dima(reference_curve_angles, p), label = label, linewidth = 2)

  p = 0.3
  label = "Dimas's hole-ice model, p = 0.3"
  ax.plot(np.cos(reference_curve_angles * 2 * np.pi / 360.0), reference_curve_dima(reference_curve_angles, p), label = label, linewidth = 2)

  # p = 0.4
  # label = "Dimas's hole-ice model, p = 0.4"
  # ax.plot(np.cos(reference_curve_angles * 2 * np.pi / 360.0), reference_curve_dima(reference_curve_angles, p), label = label, linewidth = 2)


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
  if args.pencil_beam:
    p_0 = 0.045007900000000003 # pencil beam
  else:
    p_0 = 0.0039667 # plane waves


  sensitivity = []
  sensitivity_error = []

  for i, angle in enumerate(angles):
    n = data[data.angle == angle]["photons"].sum()
    k_i = data[data.angle == angle]["hits"].sum()
    if args.hole_ice:
      p_i = reference_curve_hole_ice(angle) * p_0
    else:
      p_i = reference_curve_no_hole_ice(angle) * p_0

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
  if args.hole_ice:
    if args.llh:
      label = "hole-ice simulation, $\lambda_\mathrm{e}$=" + str_round(simulation_options["hole_ice_effective_scattering_length"]) + "m, $r$=" + str_round(simulation_options["hole_ice_radius"]) + "m, LLH = " + str_round(ln_likelihood)
    else:
      label = "hole-ice simulation, $\lambda_\mathrm{e}$=" + str_round(simulation_options["hole_ice_effective_scattering_length"]) + "m, $r$=" + str_round(simulation_options["hole_ice_radius"]) + "m"
  else:
    if args.h2_reference_curve:
      if args.pencil_beam:
        if args.direct_detection:
          label = "simulation with direct detection, pencil beam, without hole ice"
        else:
          label = "simulation pencil beam, without hole ice, without direct detection"
      else:
        if args.direct_detection:
          label = "simulation with direct detection, plane waves, without hole ice"
        else:
          label = "simulation plane waves, without hole ice, without direct detection"
    else:
      label = os.path.dirname(data_dir)

  ax.errorbar(np.cos(angles * 2 * np.pi / 360.0), sensitivity, fmt = "-o", yerr = sensitivity_error, label = label) #, linewidth=6, color = "r")

ax.set(xlabel = "cos($\eta$)")
ax.set(ylabel = "relative sensitivity")

if args.log_scale:
  ax.set(yscale = "log", ylim = [0.001, 1])
else:
  ax.set(ylim = [0, 1])

ax.legend(loc = "best")
ax.grid()

ax.set_title("Angular acceptance")

plt.show()