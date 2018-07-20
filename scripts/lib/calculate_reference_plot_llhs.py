#!/usr/bin/env python

# Calculate log likelihood (LLH) for reference angular acceptance curve vs. simulation.
# https://github.com/fiedl/hole-ice-study/issues/12

# Usage: ./calculate_reference_plot_llhs.py ~/hole-ice-study/results/parameter_scan

# This will calculate the LLH for each run within the given data directory
# and append the "llh" to the "options.json" files within.

import cli
import options
import reference_curve_llh

print "Calculating reference-curve LLHs"

for data_dir in cli.data_dirs():
  print "  " + data_dir

  opts = options.read(data_dir)

  if "llh" in opts:
    llh = opts["llh"]
  else:
    llh = reference_curve_llh.calculate(data_dir)
    options.append(data_dir, {"llh": llh})

  print "    LLH = " + str(llh)
