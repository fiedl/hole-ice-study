#!/usr/bin/env python

# Plot hits for each DOM separately.
# https://github.com/fiedl/hole-ice-study/issues/59#issuecomment-385670738

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

import os

import matplotlib as mpl
from matplotlib.mlab import griddata
from matplotlib import ticker
import matplotlib.pyplot as plt

import cli
import options
import flasher_data
import simulation_data

receiving_strings = [62, 54, 55, 64, 71, 70] # + [61, 53, 44, 45, 46, 56, 65, 72, 78, 77, 76, 69]
doms = range(1, 60)

flasher_scaling = flasher_data.scaling()
flasher_data_table = flasher_data.all()

data_hits = []
for string in receiving_strings:
  for dom in doms:
    k_data = flasher_data_table[flasher_data_table.string_number == string][flasher_data_table.dom_number == dom]["charge"].sum()
    if (k_data > 0):
      data_hits.append(k_data)

fig, ax = plt.subplots(1, 1, facecolor="white")

ax.plot(data_hits, label = "data 2012")


for data_dir in cli.data_dirs():
  simulation_options = options.read(data_dir)
  simulation_scaling = options.scaling(data_dir)
  simulation_scaling_factor = 1.0 * flasher_scaling / simulation_scaling
  simulation_data_table = simulation_data.flasher_hits(data_dir)

  simulation_hits = []
  for string in receiving_strings:
    for dom in doms:
      k_data = flasher_data_table[flasher_data_table.string_number == string][flasher_data_table.dom_number == dom]["charge"].sum()
      k_simulation = simulation_data_table[simulation_data_table.string_number == string][simulation_data_table.dom_number == dom]["charge"].sum()
      if (k_data > 0): # or (k_simulation > 0):
        data_hits.append(k_data)
        simulation_hits.append(k_simulation * simulation_scaling_factor)

  # log likelihood
  llh = simulation_options["llh"]

  # ax.plot(simulation_hits, label = "simulation with standard-clsim hole-ice approximation")
  ax.plot(simulation_hits, label = "simulation: " + "esca = " + str(simulation_options["effective_scattering_length"]) + "m, r = " + str(simulation_options["hole_ice_radius_in_dom_radii"]) + " r_DOM")
  ax.set_ylabel("number of hits")

  #ax.legend(loc = "upper right")
  ax.set_xlabel("DOM, strings " + ', '.join([str(x) for x in receiving_strings]))
  ax.set_title("Flasher study: Simulation vs. data, LLH = " + str(llh))

  output_file = os.path.join(data_dir, "flasher_hits_vs_simulation.png")
  #plt.savefig(output_file, bbox_inches='tight')

  print "=> " + output_file + "\n"
  #os.system("open '" + output_file + "'")

plt.show()