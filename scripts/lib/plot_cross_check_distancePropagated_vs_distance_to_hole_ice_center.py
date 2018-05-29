#!/usr/bin/env python

# See: https://github.com/fiedl/hole-ice-study/issues/71

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

import sys
import pandas

data_file = "~/hole-ice-study/results/cross_checks/cross_check_71.txt"
#data_file = "~/hole-ice-study/scripts/FiringRange/tmp/cross_check.txt"
data = pandas.read_csv(data_file, delim_whitespace = True, names = ["cross", "check", "when", "key",  "equals", "distancePropagated", "squared_distance_to_hole_ice_center"])

data = data[data.key == "distancePropagated_and_squared_distance_to_hole_ice_center"]

import numpy as np
import matplotlib.pyplot as plt

def str_round(number):
  return "{:.4f}".format(number)


range_min = 0.0
range_max = 2.0

true_hole_ice_radius = 0.5

# cuts
data = data[data.squared_distance_to_hole_ice_center >= range_min**2][data.squared_distance_to_hole_ice_center <= range_max**2]


# prepare canvas
fig, ax = plt.subplots(1, 1, facecolor="white")

distancePropagated = data["distancePropagated"]
squared_distance_to_hole_ice_center = data["squared_distance_to_hole_ice_center"]
distance_to_hole_ice_center = np.sqrt(squared_distance_to_hole_ice_center)

ax.plot(distance_to_hole_ice_center, distancePropagated, 'o')

ax.set_xlim(xmax = range_max)
ax.set_xlabel("distance to hole-ice center [m]")
ax.set_ylabel("distance to next scattering point [m]")

plt.show()



bins = 50
bin_width = (range_max - range_min) * 1.0 / bins
x = np.arange(range_min, range_max, bin_width) + bin_width / 2
y = list(data[(data.squared_distance_to_hole_ice_center > (x - bin_width / 2)**2) & (data.squared_distance_to_hole_ice_center <= (x + bin_width / 2)**2)]["distancePropagated"].mean() for x in x)
yerr = list(data[(data.squared_distance_to_hole_ice_center > (x - bin_width / 2)**2) & (data.squared_distance_to_hole_ice_center <= (x + bin_width / 2)**2)]["distancePropagated"].std() for x in x)


# prepare canvas
fig, ax = plt.subplots(1, 1, facecolor="white")

distancePropagated = data["distancePropagated"]
squared_distance_to_hole_ice_center = data["squared_distance_to_hole_ice_center"]
distance_to_hole_ice_center = np.sqrt(squared_distance_to_hole_ice_center)

ax.errorbar(x, y, yerr = yerr, fmt = 'ro')

mean_inside = data[data.squared_distance_to_hole_ice_center < true_hole_ice_radius**2]["distancePropagated"].mean()
mean_outside = data[data.squared_distance_to_hole_ice_center > true_hole_ice_radius**2]["distancePropagated"].mean()
ax.axhline(mean_inside, xmin = 0, xmax = true_hole_ice_radius / (range_max - range_min))
ax.axhline(mean_outside, xmin = true_hole_ice_radius / (range_max - range_min), xmax = 1)

ax.set_xlim(xmax = range_max)
ax.set_ylim(ymin = 0.0)

ax.set_xlabel("distance to hole-ice center [m]")
ax.set_ylabel("distance to next scattering point [m]")

plt.show()