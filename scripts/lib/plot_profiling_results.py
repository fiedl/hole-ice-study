#!/usr/bin/env python

import sys
import pandas

import os
import glob2

import matplotlib as mpl
from matplotlib.mlab import griddata
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

def str_round(number):
  return "{:.4f}".format(number)

data_file = sys.argv[1]
data = pandas.read_csv(data_file, delim_whitespace = True, names = ["PROFILING", "key", "time"])
keys = data["key"].unique()

print keys
print data

# cut strangly large values
data = data[data.time < 1000]

import numpy as np
import matplotlib.pyplot as plt


# prepare canvas
fig, ax = plt.subplots(1, 1, facecolor="white")

for key in keys:
  times = data[data.key == key]["time"]
  print [key, times.count()]

  num_of_bins = 200

  mean = times.mean(); stddeviation = times.std()
  label = key + ", " + str_round(mean) + '$\pm$' + str_round(stddeviation)
  n, bins, patches = ax.hist(times, range = [0, 1000], bins = num_of_bins, label = label, alpha = 0.5)

ax.set_xlabel("duration per scattering step [clock ticks]")
ax.grid()
ax.legend(loc = "best")

#ax.set_xscale("log")
#axes[1].set_ylim(ymax = 1e4)

#fig.suptitle("Cross check #66: Photons passing through hole ice, number of photons = " + str(number_of_photons), fontsize = 14)

plt.show()



# prepare canvas
fig, ax = plt.subplots(1, 1, facecolor="white")

for key in keys:
  times = data[data.key == key]["time"]
  print [key, times.count()]

  num_of_bins = 60

  mean = times.mean(); stddeviation = times.std()
  label = key + ", " + str_round(mean) + '$\pm$' + str_round(stddeviation)
  n, bins, patches = ax.hist(times, range = [0, 60], bins = num_of_bins, label = label, alpha = 0.5)

ax.set_xlabel("duration per scattering step [clock ticks]")
ax.grid()
ax.legend(loc = "best")

#ax.set_xscale("log")
#axes[1].set_ylim(ymax = 1e4)

#fig.suptitle("Cross check #66: Photons passing through hole ice, number of photons = " + str(number_of_photons), fontsize = 14)

plt.show()


# prepare canvas
fig, ax = plt.subplots(1, 1, facecolor="white")

# pie chart
# https://matplotlib.org/examples/pie_and_polar_charts/pie_demo_features.html

labels = []
sizes = []
for key in keys:
  times = data[data.key == key]["time"]
  mean = times.mean(); stddeviation = times.std()
  label = key + ", " + str_round(mean) + '$\pm$' + str_round(stddeviation)

  sizes.append(mean)
  labels.append(label)

#labels = ["add ice layers", "add hole ice", "sort", "media loop", "rest of the scattering step"]
#explode = (0.3, 0.3, 0.3, 0.3, 0)
explode = (0.3, 0)

# The last value is the total time, i.e. includes the others.
# Thus, need to subtract the others in the pie chart.
print sizes
sizes[-1] = sizes[-1] - np.sum(sizes[:-1])
print sizes

ax.pie(sizes, labels=labels, explode=explode, autopct='%1.1f%%', shadow=True, startangle=90)
ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.show()

