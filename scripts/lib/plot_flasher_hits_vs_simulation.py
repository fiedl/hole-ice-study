#!/usr/bin/env python

# Plot hits for each DOM separately.
# https://github.com/fiedl/hole-ice-study/issues/59#issuecomment-385670738

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

import sys
import pandas

flasher_data_file = "~/icecube/flasher-data/oux.63_30"
flasher_data = pandas.read_csv(flasher_data_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"])
flasher_brightness = 127
flasher_width = 127

import os
import glob2

base_path = sys.argv[1]
simulation_data_files = list(glob2.glob(os.path.join(os.path.expanduser(base_path), "./**/hits.txt")))

import json
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

import matplotlib as mpl
from matplotlib.mlab import griddata
from matplotlib import ticker
import matplotlib.pyplot as plt

for simulation_data_file in simulation_data_files:
  simulation_data = pandas.read_csv(simulation_data_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"], header = 1)

  simulation_options_file = os.path.join(os.path.dirname(simulation_data_file), "options.json")
  simulation_options = json.load(open(simulation_options_file))

  receiving_strings = [62, 54, 55, 64, 71, 70] # + [61, 53, 44, 45, 46, 56, 65, 72, 78, 77, 76, 69]
  doms = range(1, 60)

  flasher_scaling = flasher_brightness * flasher_width * 1
  simulation_scaling = simulation_options["brightness"] * simulation_options["width"] * simulation_options["thinning_factor"]
  simulation_scaling_factor = 1.0 * flasher_scaling / simulation_scaling

  data_hits = []
  simulation_hits = []
  for string in receiving_strings:
    for dom in doms:
      k_data = flasher_data[flasher_data.string_number == string][flasher_data.dom_number == dom]["charge"].sum()
      k_simulation = simulation_data[simulation_data.string_number == string][simulation_data.dom_number == dom]["charge"].sum()
      if (k_data > 0): # or (k_simulation > 0):
        data_hits.append(k_data)
        simulation_hits.append(k_simulation * simulation_scaling_factor)

  # log likelihood
  llh = agreement(flasher_data, simulation_data, flasher_scaling, simulation_scaling)

  # Plot this data point
  fig, ax = plt.subplots(1, 1, facecolor="white")

  ax.plot(data_hits, label = "data 2012")
  ax.plot(simulation_hits, label = "simulation: " + "esca = " + str(simulation_options["effective_scattering_length"]) + "m, r = " + str(simulation_options["hole_ice_radius_in_dom_radii"]) + " r_DOM")
  ax.set_ylabel("number of hits")

  ax.legend(loc = "upper right")
  ax.set_xlabel("DOM, strings " + ', '.join([str(x) for x in receiving_strings]))
  ax.set_title("Flasher study: Simulation vs. data, LLH = " + str(llh))

  output_file = os.path.join(os.path.dirname(simulation_data_file), "flasher_hits_vs_simulation.png")
  plt.savefig(output_file, bbox_inches='tight')

  print "=> " + output_file + "\n"
  os.system("open '" + output_file + "'")

