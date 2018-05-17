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
num_of_bins = 50

def str_round(number):
  return "{:.4f}".format(number)

distance_to_hole_ice_center_for_each_propagation_step = np.sqrt(data[data.when == "PROPAGATION"][data.key == "squared_distance_to_hole_ice_center"]["value"])
distance_to_hole_ice_center_on_absorption = np.sqrt(data[data.when == "ABSORPTION"][data.key == "squared_distance_to_hole_ice_center"]["value"])

for ax in axes:

  bin_width = (range_max - range_min) / num_of_bins
  bin_shift = -0.001
  bins = np.concatenate(([range_min], (np.arange(bin_width, range_max, bin_width) + bin_shift), [range_max]))

  # histogram the data
  n = ax.hist(distance_to_hole_ice_center_for_each_propagation_step, bins = bins, range = plot_range, label = 'simulation data, hole-ice radius = ' + str_round(true_hole_ice_radius) + 'm, on each scattering step')
  x = bins[0:-1] + bin_width / 2

  #n, bins, patches = ax.hist(distance_to_hole_ice_center_on_absorption, bins = bins, range = plot_range, label = 'simulation data, hole-ice radius = ' + str(true_hole_ice_radius) + 'm, on absorption')

  # plot the min distance
  ax.plot(distance_to_hole_ice_center_for_each_propagation_step.min(), 0, 'o', label = 'smallest recorded distance to hole-ice center = ' + str_round(distance_to_hole_ice_center_for_each_propagation_step.min()) + 'm')

  ax.set_xlabel("distance to hole-ice center [m]")

  ax.grid()
  ax.legend(loc = "upper right")

axes[0].set_ylim(ymax = 900)
axes[1].set_yscale("log")
axes[1].set_ylim(ymax = 2e3)

number_of_photons = distance_to_hole_ice_center_on_absorption.count()
fig.suptitle("Cross check #67: Shooting photons onto hole-ice cylinder with instant absorption, number of photons = " + str(number_of_photons), fontsize = 14)

plt.show()