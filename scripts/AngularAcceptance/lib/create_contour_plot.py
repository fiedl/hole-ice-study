import sys
import pandas

import matplotlib as mpl
from matplotlib.mlab import griddata
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

data_files = sys.argv[1:]

# prepare canvas
fig, axes = plt.subplots(1, len(data_files), facecolor="white", squeeze=False)

# determine max z range in order to use the same z range in all sub plots
data = pandas.concat(map(lambda file: pandas.read_csv(file, delim_whitespace=True), data_files))
min_z = data["agreement"].min()
max_z = data["agreement"].max()

contours = []
for index, data_file in enumerate(data_files):
  data = pandas.read_csv(data_file, delim_whitespace=True)

  # extract data run title
  title = data_file.split("/")[-2]

  # extract data
  x = data["hole_ice_radius_in_dom_radii"]
  y = data["effective_scattering_length"]
  z = data["agreement"]

  # define grid
  xi = np.linspace(data["hole_ice_radius_in_dom_radii"].min(), data["hole_ice_radius_in_dom_radii"].max(), 100)
  yi = np.linspace(data["effective_scattering_length"].min(), data["effective_scattering_length"].max(), 100)

  # grid the data
  zi = griddata(x, y, z, xi, yi, interp='linear')

  # subplot
  ax = axes[0][index]

  # contour the gridded data, plotting dots at the nonuniform data points.
  ax.contour(xi, yi, zi, 15, linewidths=0.5, colors='k')
  #cf0 = ax0.contourf(xi, yi, zi, 15, locator=ticker.LogLocator())
  #cf0 = ax0.contourf(xi, yi, zi, np.arange(0, 300, 5), extend='max')
  #cf0 = ax.contourf(xi, yi, zi, 15, vmax=max_z, vmin=-max_z)
  #cf0 = ax.contourf(xi, yi, zi, 15)
  cf0 = ax.contourf(xi, yi, zi, 15, vmax=max_z, vmin=min_z, extend='both')
  contours.append(cf0)

  # confidence intervals
  z_best = np.min(z)
  z_1_sigma = z_best + 0.5
  z_2_sigma = z_best + 2.0
  z_3_sigma = z_best + 4.5
  cf1 = ax.contour(xi, yi, zi, [z_1_sigma, z_2_sigma, z_3_sigma], colors=['#ff0000', '#cc0000', '#aa0000'])

  # plot data points.
  ax.scatter(x, y, marker='o', s=5, zorder=10)

  # sub title
  ax.set_title(title, fontsize=11)

  # labels
  ax.set(xlabel = 'hole-ice column radius [r_DOM]', ylabel = 'effective scattering length [m]')

# draw colorbar
# https://matplotlib.org/examples/api/colorbar_only.html
fig.subplots_adjust(right=0.8)
cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
norm = mpl.colors.Normalize(vmin = min_z, vmax = max_z)
cb0 = mpl.colorbar.ColorbarBase(cbar_ax, norm = norm, orientation = 'vertical')

# plot title
fig.suptitle('Agreement of hole-ice simulation and reference angular acceptance', fontsize=14)

plt.show()