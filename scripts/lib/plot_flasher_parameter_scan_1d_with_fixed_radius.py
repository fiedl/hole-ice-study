#!/usr/bin/env python

# https://github.com/fiedl/hole-ice-study/issues/92

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

fixed_radius_in_dom_radii = 0.5 # Swedish camera

import matplotlib as mpl
from matplotlib.mlab import griddata
from matplotlib import ticker
import matplotlib.pyplot as plt

import cli
import options
import flasher_data
import simulation_data


parameters_esca = []
parameters_r_r_dom = []
agreements = []

for data_dir in cli.data_dirs():
  simulation_options = options.read(data_dir)

  if simulation_options["hole_ice_radius_in_dom_radii"] == fixed_radius_in_dom_radii:
    llh = simulation_options["llh"]

    if llh < 0:
      parameters_esca.append(simulation_options["effective_scattering_length"])
      parameters_r_r_dom.append(simulation_options["hole_ice_radius_in_dom_radii"])
      agreements.append(llh)


import numpy as np

best_agreement = np.max(agreements)
neg_two_delta_llhs = - 2 * (np.asarray(agreements) - best_agreement)

print("best values:")
print("  LLH = " + str(best_agreement))
i = np.where(agreements == best_agreement)[0][0]
print("  esca = " + str(parameters_esca[i]) + "m")
print("  r = " + str(parameters_r_r_dom[i]) + " r_dom")

import matplotlib as mpl
from matplotlib.mlab import griddata
from matplotlib import ticker
import matplotlib.pyplot as plt

# prepare canvas
fig, ax = plt.subplots(1, 1, facecolor="white")

# extract data
x = parameters_esca
y = agreements

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

ax.plot(x, y, "o")
ax.set(xlabel = 'effective scattering length [m]', ylabel = "$-2 \Delta \mathrm{LLH}$")
ax.set_title("Flasher data vs. simulation for $r = 0.5\,r_\mathrm{DOM}$")

#ax.set_xscale("log")

plt.show()