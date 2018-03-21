import sys
import pandas

data_file = (sys.argv[1] if (len(sys.argv) > 1) else "~/icecube/flasher-data/oux.62_30")
data = pandas.read_csv(data_file, delim_whitespace = True, names = ["string_number", "dom_number", "time", "charge"])

simulation_titles = [
  "hole-ice simulation",
  "hole-ice approximation",
  "no hole ice"
]
simulation_data_files = [
  "~/hole-ice-study/scripts/FlasherSimulation/cluster-results/Run-2018-zooz3Mek/hits.txt", # simulation
  "~/hole-ice-study/scripts/FlasherSimulation/cluster-results/Run-2018-Eisia3xu/hits.txt", # approximation
  "~/hole-ice-study/scripts/FlasherSimulation/cluster-results/Run-2018-eiweip3H/hits.txt", # no
]
simulation_plot_styles = ["bo", "go", "yo"]

import matplotlib.pyplot as plt
import numpy as np

# prepare canvas
fig, ax = plt.subplots(facecolor="white")

# extract relevant data
subplot_data = data[data.string_number == 63]
x = subplot_data["dom_number"]
y = subplot_data["charge"]

plot_x = range(subplot_data["dom_number"].min(), subplot_data["dom_number"].max())
plot_y = [0] * len(plot_x)
#plot_y_err = [0] * len(plot_x)

for i, x in enumerate(plot_x):
  y_data = subplot_data[subplot_data.dom_number == x]["charge"]
  plot_y[i] = np.sum(y_data)
  #plot_y_err[i] = np.std(y_data)

ax.set_yscale("log")
#ax.errorbar(plot_x, plot_y, yerr = plot_y_err, fmt = 'ro', label = "flasher data, 2012")

ax.plot(plot_x, plot_y, "ro", label = "flaher data 2012")

for i, simulation_title in enumerate(simulation_titles):
  simulation_data = pandas.read_csv(simulation_data_files[i], delim_whitespace = True, header = 1, names = ["string_number", "dom_number", "hits"])
  scale = subplot_data["charge"].sum() / simulation_data["hits"].sum()
  plot_x = simulation_data["dom_number"]
  plot_y = simulation_data["hits"] * scale
  ax.plot(plot_x, plot_y, simulation_plot_styles[i], label = simulation_title)

ax.set(xlabel = "DOM number on string 63", ylabel="Received charge ~ number of hits",
  title = "Minimal flasher study, emitter 62-30, receiving string 63")

ax.grid()
ax.legend(loc = "upper right")
plt.show()


