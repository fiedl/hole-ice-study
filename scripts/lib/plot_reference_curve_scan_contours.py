#!/usr/bin/env python

# Angular-acceptance parameter scan.
# https://github.com/fiedl/hole-ice-study/issues/12

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

import cli
import options

parameters_esca = []
parameters_r_r_dom = []
llhs = []

for data_dir in cli.data_dirs():
  simulation_options = options.read(data_dir)
  llh = simulation_options["llh"]
  esca = simulation_options["hole_ice_effective_scattering_length"]
  r_r_dom = simulation_options["hole_ice_radius_in_dom_radii"]

  if (llh < 0) and (esca > 0) and (r_r_dom > 0):
    parameters_esca.append(esca)
    parameters_r_r_dom.append(r_r_dom)
    llhs.append(llh)


import numpy as np

best_llh = np.max(llhs)
neg_two_delta_llhs = - 2 * (np.asarray(llhs) - best_llh)

print("best values:")
print("  LLH: " + str(best_llh))
i = np.where(llhs == best_llh)[0][0]
print("  esca = " + str(parameters_esca[i]) + "m")
print("  r = " + str(parameters_r_r_dom[i]) + " r_dom")


import matplotlib as mpl
from matplotlib.mlab import griddata
from matplotlib import ticker
import matplotlib.pyplot as plt


# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

# prepare canvas
fig, ax = plt.subplots(1, 1, facecolor="white")

# extract data
x = parameters_r_r_dom
y = parameters_esca
z = neg_two_delta_llhs

# define grid
xi = np.linspace(np.min(x), np.max(x), 100)
yi = np.linspace(np.min(y), np.max(y), 100)

# grid the data
zi = griddata(x, y, z, xi, yi, interp='linear')

cf0 = ax.contourf(xi, yi, zi, 15, locator = mpl.ticker.LogLocator())
#cf0 = ax.contourf(xi, yi, zi, 50)#, vmax = 1000)
# cf0 = ax.contourf(xi, yi, zi, 15, vmax = 15, extend = 'max') #, vmax=1.5e6)
# clev = np.arange(z.min(), 15, 1)
# cf0 = ax.contourf(xi, yi, zi, clev, extend = 'max')

cbar = plt.colorbar(cf0)
cbar.ax.set_ylabel("$-2 \Delta \mathrm{LLH}$")

# plot data points.
ax.scatter(x, y, marker='o', s=1, zorder=10)

# labels
ax.set_title("Angular-acceptance parameter scan: binomial LLH (simulation vs reference curve)")
ax.set(xlabel = 'hole-ice column radius [r_DOM]', ylabel = 'effective scattering length [m]')

plt.show()