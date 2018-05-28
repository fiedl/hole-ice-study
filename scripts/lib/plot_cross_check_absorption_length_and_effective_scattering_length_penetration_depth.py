#!/usr/bin/env python

# See: https://github.com/fiedl/hole-ice-study/issues/71

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

import sys
import pandas

data_file = "~/hole-ice-study/results/cross_checks/cross_check_72.txt"
data = pandas.read_csv(data_file, delim_whitespace = True, names = ["cross", "check", "when", "key", "x", "y", "z"])

import numpy as np
import matplotlib.pyplot as plt

def str_round(number):
  return "{:.4f}".format(number)

# cuts
hole_ice_radius = 0.5
hole_ice_x = -256.02301025390625
hole_ice_y = -521.281982421875
hole_ice_border_x = hole_ice_x - hole_ice_radius
data = data[data.when == "ABSORPTION"][data.key == "x,y,z"]
data = data[(data.x - hole_ice_x)**2 + (data.y - hole_ice_y)**2 < hole_ice_radius**2]
#data = data[data.x > hole_ice_border_x][data.x < hole_ice_border_x + hole_ice_radius * 2]
#data = data[data.y > hole_ice_y - hole_ice_radius][data.y < hole_ice_y + hole_ice_radius]

absorption_penetration_depth = data["x"] - hole_ice_border_x


data_file = "~/hole-ice-study/results/cross_checks/cross_check_72_scat.txt"
data = pandas.read_csv(data_file, delim_whitespace = True, names = ["cross", "check", "when", "key", "x", "y", "z"])
data = data[data.when == "ABSORPTION"][data.key == "x,y,z"]
data = data[(data.x - hole_ice_x)**2 + (data.y - hole_ice_y)**2 < hole_ice_radius**2]
scattering_penetration_depth = data["x"] - hole_ice_border_x


# prepare canvas
fig, ax = plt.subplots(1, 1, facecolor="white")

ax.hist(absorption_penetration_depth, normed = False, bins = 50, label = "absorption", alpha = 0.5)
ax.hist(scattering_penetration_depth, normed = False, bins = 50, label = "effective scattering", alpha = 0.5)

ax.legend(loc = "best")
ax.set_xlabel("Penetration depth [m]")

plt.show()