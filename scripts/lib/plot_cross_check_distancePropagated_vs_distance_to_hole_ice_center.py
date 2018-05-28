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

# prepare canvas
fig, ax = plt.subplots(1, 1, facecolor="white")

distancePropagated = data["distancePropagated"]
squared_distance_to_hole_ice_center = data["squared_distance_to_hole_ice_center"]
distance_to_hole_ice_center = np.sqrt(squared_distance_to_hole_ice_center)

ax.plot(distance_to_hole_ice_center, distancePropagated, 'o')

ax.set_xlim(xmax = 5.0)
ax.set_xlabel("distance to hole-ice center [m]")
ax.set_ylabel("distance to next scattering point [m]")

plt.show()