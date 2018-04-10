#!/usr/bin/env python

# Usage:
# python calculate_agreement.py ~/hole-ice-study/results/parameter_scan

import sys
import pandas

data_root_folder = sys.argv[1]

import os
import glob2

options_files = glob2.glob(os.path.join(data_root_folder, "./**/options.txt"))
data_dirs = list((os.path.dirname(options_file) for options_file in options_files))

import scipy.special
import numpy as np

def reference_curve(angle):
  x = np.cos(2 * np.pi * angle / 360.0)
  a = 0.32813; b = 0.63899; c = 0.20049; d =-1.2250; e =-0.14470; f = 4.1695;
  g = 0.76898; h =-5.8690; i =-2.0939; j = 2.3834; k = 1.0435;
  return a + b*x + c*x**2 + d*x**3 + e*x**4 + f*x**5 + g*x**6 + h*x**7 + i*x**8 + j*x**9 + k*x**10

neg_ln_likelihoods = []

for data_dir in data_dirs:
  data_files = glob2.glob(os.path.join(data_dir, "./angle_hits_and_photons_*.txt"))
  data_rows = (pandas.read_csv(data_file, delim_whitespace = True, names = ["angle", "hits", "photons"]) for data_file in data_files)
  data = pandas.concat(data_rows, ignore_index = True)

  # Calculate the ln_likelihood, i.e. the probability of data matching the
  # reference curve at all angles.
  #
  # See: https://github.com/fiedl/hole-ice-study/issues/12#issuecomment-376179961
  #
  angles = data["angle"].unique()
  ln_likelihood_summands = [0] * len(angles)

  # Gauge factor
  #
  # See: https://github.com/fiedl/hole-ice-study/issues/12#issuecomment-376580354
  #
  p_0 = 0.0039667 # plane waves
  #p_0 = 0.045007900000000003 # pencil beam

  for i, angle in enumerate(angles):
    n = data[data.angle == angle]["photons"].sum()
    k_i = data[data.angle == angle]["hits"].sum()
    p_i = reference_curve(angle) * p_0

    ln_binomial_coefficient = \
        scipy.special.gammaln(n + 1) - scipy.special.gammaln(k_i + 1) - scipy.special.gammaln(n - k_i + 1)

    ln_likelihood_summands[i] = \
        ln_binomial_coefficient + k_i * np.log(p_i) + (n - k_i) * np.log(1 - p_i)

  ln_likelihood = sum(ln_likelihood_summands)

  print("Writing " + str(ln_likelihood) + " to " + data_dir + "/ln_likelihood.txt.")
  export_file = open(data_dir + "/ln_likelihood.txt", "w")
  export_file.write(str(ln_likelihood))
  export_file.close()

  neg_ln_likelihood = - ln_likelihood
  neg_ln_likelihoods.append(neg_ln_likelihood)

best_index = neg_ln_likelihoods.index(min(neg_ln_likelihoods))
print("\nbest neg ln likelihood:")
print(neg_ln_likelihoods[best_index])
print(data_dirs[best_index])

