import sys
import pandas

data_file = sys.argv[1]
data = pandas.read_csv(data_file, delim_whitespace=True)

import matplotlib.pyplot as plt
import numpy as np

# prepare canvas
fig, (ax0, ax1) = plt.subplots(2, 1, facecolor="white")

#for r in data["hole_ice_radius_in_dom_radii"].unique():
for r in [0.1, 0.5, 1.0, 2.0]:

  subplot_data = data[data.hole_ice_radius_in_dom_radii == r]

  x = subplot_data["effective_scattering_length"]
  y = subplot_data["agreement"]

  # line plot
  ax0.semilogy(x, y, label = "hole-ice radius = " + str(r) + " dom radii")

  # labels
  ax0.set(xlabel = "effective scattering length [m]", ylabel="Reduced chi squared",
      title = "Agreement of data and reference")

ax0.grid()
ax0.legend(loc = "upper center")


#for s in data["effective_scattering_length"].unique():
for s in [0.020000000000000004, 0.35, 1.0, 3.0]:

  subplot_data = data[data.effective_scattering_length == s]

  x = subplot_data["hole_ice_radius_in_dom_radii"]
  y = subplot_data["agreement"]

  # line plot
  ax1.semilogy(x, y, label = "effective scattering length = " + str(round(s, 2)) + "m")

  # labels
  ax1.set(xlabel = "hole-ice radius [dom radii]", ylabel="Reduced chi squared")

ax1.grid()
ax1.legend(loc = "upper center")

plt.show()