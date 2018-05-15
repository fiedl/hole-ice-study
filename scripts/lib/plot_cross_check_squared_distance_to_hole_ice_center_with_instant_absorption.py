#!/usr/bin/env python

# See: https://github.com/fiedl/hole-ice-study/issues/67

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

import sys
import pandas

data_file = "~/hole-ice-study/results/cross_checks/cross_check_67.txt"
#data_file = "~/hole-ice-study/scripts/FiringRange/tmp/cross_check.txt"
data = pandas.read_csv(data_file, delim_whitespace = True, names = ["cross", "check", "when", "key", "equals", "value"])

import numpy as np
import matplotlib.pyplot as plt

# prepare canvas
fig, axes = plt.subplots(1, 2, facecolor="white")

true_hole_ice_radius = 0.5

range_min = 0.0
range_max = 2.0
plot_range = (range_min, range_max)
num_of_bins = 100

distance_to_hole_ice_center_for_each_propagation_step = np.sqrt(data[data.when == "PROPAGATION"][data.key == "squared_distance_to_hole_ice_center"]["value"])
distance_to_hole_ice_center_on_absorption = np.sqrt(data[data.when == "ABSORPTION"][data.key == "squared_distance_to_hole_ice_center"]["value"])

for ax in axes:

  # histogram the data
  n, bins, patches = ax.hist(distance_to_hole_ice_center_for_each_propagation_step, bins = num_of_bins, range = plot_range, label = 'simulation data, hole-ice radius = ' + str(true_hole_ice_radius) + 'm, on each scattering step')
  bin_width = (range_max - range_min) / num_of_bins
  x = bins[0:-1] + bin_width / 2

  n, bins, patches = ax.hist(distance_to_hole_ice_center_on_absorption, bins = num_of_bins, range = plot_range, label = 'simulation data, hole-ice radius = ' + str(true_hole_ice_radius) + 'm, on absorption')

  ax.set_xlabel("distance to hole-ice center [m]")

  ax.grid()
  ax.legend(loc = "upper right")

axes[1].set_yscale("log")

number_of_photons = distance_to_hole_ice_center_on_absorption.count()
fig.suptitle("Cross check #67: Shooting photons onto hole-ice cylinder with instant absorption, number of photons = " + str(number_of_photons), fontsize = 14)

plt.show()