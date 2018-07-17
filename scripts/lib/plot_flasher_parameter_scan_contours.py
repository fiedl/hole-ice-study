#!/usr/bin/env python

# See: https://github.com/fiedl/hole-ice-study/issues/57#issuecomment-385347525

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

import sys
import pandas

flasher_data_file = "~/icecube/flasher-data/oux.63_30"
flasher_data = pandas.read_csv(flasher_data_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"])
flasher_brightness = 127
flasher_width = 127

import os
import glob2

simulation_data_folder = sys.argv[1]

if not simulation_data_folder:
  simulation_data_folder = "~/hole-ice-study/results/flasher_parameter_scan"
simulation_data_files = list(glob2.glob(os.path.join(os.path.expanduser(simulation_data_folder), "./**/hits.txt")))

import numpy as np
import scipy, scipy.special

# https://github.com/thoglu/mc_uncertainty/blob/master/llh_defs/poisson.py
#
def poisson_equal_weights(k,k_mc,avgweights,prior_factor=0.0):
       return (scipy.special.gammaln((k+k_mc+prior_factor)) -scipy.special.gammaln(k+1.0)-scipy.special.gammaln(k_mc+prior_factor) + (k_mc+prior_factor)* np.log(1.0/avgweights) - (k_mc+k+prior_factor)*np.log(1.0+1.0/avgweights)).sum()

# Calculate agreement of data and simulation using a likelihood function.
# The `agreement` is a log likelihood (LLH).
#
def agreement(flasher_data, simulation_data, flasher_scaling, simulation_scaling):
  #receiving_strings = [62, 54, 55, 64, 71, 70]
  #receiving_strings = [62, 54]
  receiving_strings = [55, 64, 71, 70]
  doms = range(1, 60)

  k = []
  k_mc = []
  weights = []
  for string in receiving_strings:
    for dom in doms:
      data_number_of_hits = flasher_data[flasher_data.string_number == string][flasher_data.dom_number == dom]["charge"].sum()
      simulation_number_of_hits = simulation_data[simulation_data.string_number == string][simulation_data.dom_number == dom]["charge"].sum()

      if (data_number_of_hits > 0) and (simulation_number_of_hits > 0):
        k.append(data_number_of_hits)
        k_mc.append(simulation_number_of_hits)
        weights.append(1.0 * flasher_scaling / simulation_scaling)

  if len(k_mc) > 10:
    return poisson_equal_weights(np.asarray(k), np.asarray(k_mc), np.asarray(weights))
  else:
    return -np.inf


import json

parameters_esca = []
parameters_r_r_dom = []
agreements = []

for simulation_data_file in simulation_data_files:
  simulation_data = pandas.read_csv(simulation_data_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"], header = 1)
  simulation_options_file = os.path.join(os.path.dirname(simulation_data_file), "options.json")
  simulation_options = json.load(open(simulation_options_file))

  flasher_scaling = flasher_brightness * flasher_width * 1
  simulation_scaling = simulation_options["brightness"] * simulation_options["width"] * simulation_options["thinning_factor"]
  a = agreement(flasher_data, simulation_data, flasher_scaling, simulation_scaling)

  if a < 0:
    parameters_esca.append(simulation_options["effective_scattering_length"])
    parameters_r_r_dom.append(simulation_options["hole_ice_radius_in_dom_radii"])
    agreements.append(a)

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

best_agreement = np.max(agreements)
neg_two_delta_llhs = - 2 * (np.asarray(agreements) - best_agreement)

print("best values:")
print("  agreement: " + str(best_agreement))
i = np.where(agreements == best_agreement)[0][0]
print("  esca = " + str(parameters_esca[i]) + "m")
print("  r = " + str(parameters_r_r_dom[i]) + " r_dom")

import matplotlib as mpl
from matplotlib.mlab import griddata
from matplotlib import ticker
import matplotlib.pyplot as plt

# prepare canvas
fig, ax = plt.subplots(1, 1, facecolor="white")

# extract data
x = parameters_r_r_dom
y = parameters_esca
z = neg_two_delta_llhs

# define grid
xi = np.linspace(np.min(x), np.max(x), 100)
yi = np.linspace(np.min(y), np.max(y), 100)

# grid the data
zi = griddata(x, y, z, xi, yi, interp='linear')

cf0 = ax.contourf(xi, yi, zi, 15)
# cf0 = ax.contourf(xi, yi, zi, 15, vmax = 15, extend = 'max') #, vmax=1.5e6)
# clev = np.arange(z.min(), 15, 1)
# cf0 = ax.contourf(xi, yi, zi, clev, extend = 'max')

cbar = plt.colorbar(cf0)
cbar.ax.set_ylabel("$-2 \Delta \mathrm{LLH}$")

# plot data points.
ax.scatter(x, y, marker='o', s=5, zorder=10)

# labels
ax.set_title("Flasher parameter scan: LLH (simulation vs data), poisson equal weights")
ax.set(xlabel = 'hole-ice column radius [r_DOM]', ylabel = 'effective scattering length [m]')

plt.show()