import sys
import pandas

data_file = (sys.argv[1] if (len(sys.argv) > 1) else "~/icecube/flasher-data/oux.62_30")
data = pandas.read_csv(data_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"])

simulation_titles = [
  "hole-ice simulation all leds",
  "hole-ice simulation",
#  "hole-ice approximation",
#  "no hole ice"
]
simulation_data_files = [
  "~/hole-ice-study/scripts/FlasherSimulation/cluster-results/Run-2018-paYeiy3v/hits.txt", # new simulation all leds
  "~/hole-ice-study/scripts/FlasherSimulation/cluster-results/Run-2018-zooz3Mek/read_out_hits.txt", # simulation
#  "~/hole-ice-study/scripts/FlasherSimulation/cluster-results/Run-2018-Eisia3xu/read_out_hits.txt", # approximation
#  "~/hole-ice-study/scripts/FlasherSimulation/cluster-results/Run-2018-eiweip3H/read_out_hits.txt", # no
]
simulation_plot_styles = ["bo", "go", "yo"]

import matplotlib.pyplot as plt
import numpy as np

# prepare canvas
fig, ax = plt.subplots(facecolor="white")

# extract relevant data
subplot_data = data[data.string_number == 63]
x = subplot_data["dom_number"]
#y = subplot_data["charge"]
y = subplot_data["time"]

#ax.plot(x, y, 'ro')


#fig, ax = plt.subplots(facecolor="white")

plot_x = range(subplot_data["dom_number"].min(), subplot_data["dom_number"].max())
plot_y = [0] * len(plot_x)
for i, x in enumerate(plot_x):
  charge = subplot_data[subplot_data.dom_number == x]["charge"].sum()
  y_data = subplot_data[subplot_data.dom_number == x]["time"]
  #plot_y[i] = (np.min(y_data) if charge > 1e-2 else np.nan)
  plot_y[i] = np.min(y_data)

ax.set(xlabel = "DOM number on string 63", ylabel = "Earliest arrival time [ns]",
    title = "Minimal flasher study, emitter DOM 62-30, receiving string 63")
ax.plot(plot_x, plot_y, 'ro', label = "flasher data 2012")


# plot_x = range(subplot_data["dom_number"].min(), subplot_data["dom_number"].max())
# plot_y = [0] * len(plot_x)
# #plot_y_err = [0] * len(plot_x)
#
# for i, x in enumerate(plot_x):
#   y_data = subplot_data[subplot_data.dom_number == x]["charge"]
#   plot_y[i] = np.sum(y_data)
#   #plot_y_err[i] = np.std(y_data)
#
#ax.set_yscale("log")
# #ax.errorbar(plot_x, plot_y, yerr = plot_y_err, fmt = 'ro', label = "flasher data, 2012")
#
# ax.plot(plot_x, plot_y, "ro", label = "flaher data 2012")
#
for i, simulation_title in enumerate(simulation_titles):
  simulation_data = pandas.read_csv(simulation_data_files[i], delim_whitespace = True)
  plot_y = [np.nan] * len(plot_x)
  for j, x in enumerate(plot_x):
    plot_y[j] = simulation_data[simulation_data.dom == x]["time"].min()

  #plot_x = simulation_data["dom"]
  # plot_y = simulation_data["hits"] * scale
  #plot_y = simulation_data["time"]
  ax.plot(plot_x, plot_y, simulation_plot_styles[i], label = simulation_title)
#
# ax.set(xlabel = "DOM number on string 63", ylabel="Received charge ~ number of hits",
#   title = "Minimal flasher study, emitter 62-30, receiving string 63")
#
ax.grid()
ax.legend(loc = "upper right")
plt.show()


