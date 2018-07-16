#!/usr/bin/env python

# See: https://github.com/fiedl/hole-ice-study/issues/91

import sys
import pandas
import json

import matplotlib as mpl
from matplotlib.mlab import griddata
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

data_root_folders = sys.argv[1:]

import os
import glob2

options_files = []
for data_root_folder in data_root_folders:
  options_files += glob2.glob(os.path.join(data_root_folder, "./**/options.txt"))

data_dirs = list((os.path.dirname(options_file) for options_file in options_files))

sending_string = 60
sending_dom = 30
receiving_string = 70
receiving_dom = 30

# alternative:
receiving_strings = [70, 71, 64, 55, 62 ,54]

# prepare canvas
fig, ax = plt.subplots(1, 1, facecolor="white")

weights_array = []
bins_array = []
titles_array = []

time_min = 500
time_max = 4000 # ns

def str_round(number):
  return "{:.4f}".format(number)

# Plot real flasher data as reference
plot_real_flasher_data = True
if plot_real_flasher_data:
  flasher_data_file = "~/icecube/flasher-data/oux.63_30"
  flasher_data = pandas.read_csv(flasher_data_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"])
  flasher_brightness = 127
  flasher_width = 127
  #receiver_data = flasher_data[flasher_data.string_number == receiving_string][flasher_data.dom_number == receiving_dom]
  #receiver_data = flasher_data[flasher_data.string_number != sending_string]
  receiver_data = flasher_data[flasher_data.string_number.isin(receiving_strings)]
  receiver_data = receiver_data[receiver_data.time < time_max][receiver_data.time > time_min] # cut
  bins = receiver_data["time"]
  weights = receiver_data["charge"]
  bins_array.append(bins)
  weights_array.append(weights)
  titles_array.append("Flasher data 2012")


# Plot simulation data from command line arguments
for index, data_dir in enumerate(data_dirs):
  data_file = data_dir + "/hits.txt"
  data = pandas.read_csv(data_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"], header = 1)
  #receiver_data = data[data.string_number == receiving_string][data.dom_number == receiving_dom]
  receiver_data = data[data.string_number.isin(receiving_strings)]
  receiver_data = receiver_data[receiver_data.time < time_max][receiver_data.time > time_min] # cut

  options_file = os.path.join(data_dir, "./options.json")
  simulation_options = json.load(open(options_file))


  # simulation data needs to be binned.
  bin_width = 25
  bins = range(time_min, time_max, bin_width)
  weights, time_edges = np.histogram(receiver_data["time"], bins + [max(bins) + bin_width])

  weights = weights / simulation_options.get("thinning_factor", 1.0)

  bins_array.append(bins)
  weights_array.append(weights)

  print simulation_options
  if "without_hole_ice" in data_dir:
    titles_array.append("Simulation without hole ice")
  elif "standard_clsim_hole_ice_approximation" in data_dir:
    titles_array.append("Simulation with standard-clsim hole-ice approximation")
  else:
    esca = simulation_options["effective_scattering_length"]
    r = simulation_options["hole_ice_radius_in_dom_radii"]
    titles_array.append("Simulation: $\lambda_\mathrm{e}$=" + str_round(esca) + "m, $r$=" + str_round(r) + " $r_\mathrm{DOM}$")

ax.hist(bins_array, (time_max - time_min) / 25 / 3, weights = weights_array, label = titles_array, normed = False, fill = False, histtype = "step")

ax.set_xlabel("Photon arrival time at DOM(" + str(receiving_string) + "," + str(receiving_dom) + ") after emission at DOM (63,30) [ns]")
ax.set_ylabel("Fraction of received photons [arbitrary units]")

plt.legend(loc = "best")
plt.show()
