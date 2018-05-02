#!/usr/bin/env python

# Plot hits for each DOM separately.
# https://github.com/fiedl/hole-ice-study/issues/59#issuecomment-385670738

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

import sys
import pandas

flasher_data_file = "~/icecube/flasher-data/oux.63_30"
flasher_data = pandas.read_csv(flasher_data_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"])

import os
import glob2

base_path = sys.argv[1]
simulation_data_files = list(glob2.glob(os.path.join(os.path.expanduser(base_path), "./**/hits.txt")))

import json
import numpy as np
import scipy, scipy.special

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

  flasher_data_total_hits_in_detector = flasher_data["charge"].sum()
  simulation_total_hits_in_detector = simulation_data["charge"].sum()

  data_hits = []
  simulation_hits = []
  for string in receiving_strings:
    for dom in doms:
      k_data = flasher_data[flasher_data.string_number == string][flasher_data.dom_number == dom]["charge"].sum()
      k_simulation = simulation_data[simulation_data.string_number == string][simulation_data.dom_number == dom]["charge"].sum()
      if (k_data > 0) or (k_simulation > 0):
        data_hits.append(k_data)
        simulation_hits.append(k_simulation)

  relative_data_hits = data_hits / flasher_data_total_hits_in_detector
  relative_simulation_hits = simulation_hits / flasher_data_total_hits_in_detector

  # Plot this data point
  fig, ax = plt.subplots(1, 1, facecolor="white")
  ax.plot(relative_data_hits, label = "data 2012")
  ax.plot(relative_simulation_hits, label = "simulation: " + "esca = " + str(simulation_options["effective_scattering_length"]) + "m, r = " + str(simulation_options["hole_ice_radius_in_dom_radii"]) + " r_DOM")
  ax.legend(loc = "upper right")
  ax.set_xlabel("DOM, strings " + ', '.join([str(x) for x in receiving_strings]))
  ax.set_ylabel("number of hits / total hits in detector")
  ax.set_title("Flasher study: Simulation vs. data")
  plt.show()
