import sys
import pandas

from matplotlib.mlab import griddata
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np


data_file = sys.argv[1]
data = pandas.read_csv(data_file, delim_whitespace=True)

# extract data
x = data["hole_ice_radius_in_dom_radii"]
y = data["effective_scattering_length"]
z = data["agreement"]

# define grid
xi = np.linspace(data["hole_ice_radius_in_dom_radii"].min(), data["hole_ice_radius_in_dom_radii"].max(), 100)
yi = np.linspace(data["effective_scattering_length"].min(), data["effective_scattering_length"].max(), 100)

# grid the data
zi = griddata(x, y, z, xi, yi, interp='linear')

# prepare plot canvas
fig0, ax0 = plt.subplots(facecolor='white')

# contour the gridded data, plotting dots at the nonuniform data points.
ax0.contour(xi, yi, zi, 15, linewidths=0.5, colors='k')
#cf0 = ax0.contourf(xi, yi, zi, 15, locator=ticker.LogLocator())
#cf0 = ax0.contourf(xi, yi, zi, np.arange(0, 300, 5), extend='max')
cf0 = ax0.contourf(xi, yi, zi, 15, vmax=abs(zi).max(), vmin=-abs(zi).max())

# confidence intervals
z_min = np.min(z)
z_1_sigma = z_min + 0.5
z_2_sigma = z_min + 2.0
z_3_sigma = z_min + 4.5
cf1 = ax0.contour(xi, yi, zi, [z_1_sigma, z_2_sigma, z_3_sigma], colors='red')

# draw colorbar
plt.colorbar(cf0)

# plot data points.
ax0.scatter(x, y, marker='o', s=5, zorder=10)

plt.title('Agreement of hole-ice simulation and reference angular acceptance')
plt.xlabel('hole-ice column radius [r_DOM]')
plt.ylabel('effective scattering length [m]')

plt.show()