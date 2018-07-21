#!/usr/bin/env python

# Usage
#
#     import reference_curve_llh
#     reference_curve_llh.calculate(data_dir)
#

# import code; code.interact(local=dict(globals(), **locals()))  # like binding.pry

import numpy as np
import scipy, scipy.special

import options
import simulation_data

def reference_curve(angle):
  x = np.cos(2 * np.pi * angle / 360.0)
  a = 0.32813; b = 0.63899; c = 0.20049; d =-1.2250; e =-0.14470; f = 4.1695;
  g = 0.76898; h =-5.8690; i =-2.0939; j = 2.3834; k = 1.0435;
  return a + b*x + c*x**2 + d*x**3 + e*x**4 + f*x**5 + g*x**6 + h*x**7 + i*x**8 + j*x**9 + k*x**10

def binomial_llh(k, p, n):
  return \
    ( \
    scipy.special.gammaln(n + 1) - scipy.special.gammaln(k + 1) - scipy.special.gammaln(n - k + 1) + \
    k * np.log(p) + (n - k) * np.log(1 - p) \
    ).sum()

def calculate(data_dir):
  opts = options.read(data_dir)

  # gauging: https://github.com/fiedl/hole-ice-study/issues/12#issuecomment-376580354
  #
  if ("plane_wave" in opts) and opts["plane_wave"]:
    p_0 = 0.0039667 # plane waves
  else:
    p_0 = 0.045007900000000003 # pencil beam

  # data: ["angle", "hits", "photons"]
  data = simulation_data.angular_acceptance(data_dir)
  angles = data["angle"].unique()
  k = []
  p = []
  n = []

  for i, angle in enumerate(angles):
    n_i = data[data.angle == angle]["photons"].sum()
    k_i = data[data.angle == angle]["hits"].sum()
    p_i = reference_curve(angle) * p_0

    k.append(k_i)
    p.append(p_i)
    n.append(n_i)

  k = np.asarray(k)
  n = np.asarray(n)
  p = np.asarray(p)

  return binomial_llh(k, p, n)
