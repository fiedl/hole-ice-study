#!/usr/bin/env python

# https://github.com/fiedl/hole-ice-study/issues/92

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

fixed_radius_in_dom_radii = 0.5 # Swedish camera

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

# https://github.com/thoglu/mc_uncertainty/blob/master/llh_defs/poisson.py#L11
#
def poisson_infinite_statistics(k, lambd):
  return (-lambd+k*np.log(lambd)-scipy.special.gammaln(k+1)).sum()

# Calculate agreement of data and simulation using a likelihood function.
# The `agreement` is a negative log likelihood.
#
def agreement(flasher_data, simulation_data, flasher_scaling, simulation_scaling):
  #receiving_strings = [62, 54, 55, 64, 71, 70]
  #receiving_strings = [62, 54]
  receiving_strings = [55, 64, 71, 70]
  doms = range(1, 60)

  k = []
  lambd = []
  for string in receiving_strings:
    for dom in doms:
      data_number_of_hits = flasher_data[flasher_data.string_number == string][flasher_data.dom_number == dom]["charge"].sum()
      simulation_number_of_hits = simulation_data[simulation_data.string_number == string][simulation_data.dom_number == dom]["charge"].sum()

      if (data_number_of_hits > 0) and (simulation_number_of_hits > 0):
        k.append(data_number_of_hits)
        lambd.append(simulation_number_of_hits)

  simulation_scaling_factor = 1.0 * flasher_scaling / simulation_scaling

  k = np.asarray(k) * 1.0
  lambd = np.asarray(lambd) * simulation_scaling_factor

  if len(lambd) > 10:
    return poisson_infinite_statistics(k, lambd)
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

  if simulation_options["hole_ice_radius_in_dom_radii"] == fixed_radius_in_dom_radii:
    a = agreement(flasher_data, simulation_data, flasher_scaling, simulation_scaling)

    if a < 0:
      parameters_esca.append(simulation_options["effective_scattering_length"])
      parameters_r_r_dom.append(simulation_options["hole_ice_radius_in_dom_radii"])
      agreements.append(a)

best_agreement = np.max(agreements)
gofs = np.asarray(agreements) / best_agreement

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
x = parameters_esca
y = agreements

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

ax.plot(x, y, "o")
ax.set(xlabel = 'effective scattering length [m]', ylabel = "LLH: Flasher data vs. simulation")

plt.show()