#!/usr/bin/env python

# Usage
#
#     import flasher_llh
#     flasher_llh.calculate(flasher_data, simulation_data, flasher_scaling, simulation_scaling)
#

import numpy as np
import scipy, scipy.special

# https://github.com/thoglu/mc_uncertainty/blob/master/llh_defs/poisson.py
#
def poisson_equal_weights(k,k_mc,avgweights,prior_factor=0.0):
  return (scipy.special.gammaln((k+k_mc+prior_factor)) -scipy.special.gammaln(k+1.0)-scipy.special.gammaln(k_mc+prior_factor) + (k_mc+prior_factor)* np.log(1.0/avgweights) - (k_mc+k+prior_factor)*np.log(1.0+1.0/avgweights)).sum()


import pandas

def calculate_for_data_and_sim(flasher_data, simulation_data, flasher_scaling, simulation_scaling):
  #receiving_strings = [62, 54, 55, 64, 71, 70]
  #receiving_strings = [62, 54]
  receiving_strings = [55, 64, 71, 70]
  doms = range(1, 60)

  k = []
  k_mc = []
  weights = []
  for string in receiving_strings:
    for dom in doms:
      data_number_of_hits = flasher_data[flasher_data.string_number == string][flasher_data.dom_number == dom]["charge"].sum()
      simulation_number_of_hits = simulation_data[simulation_data.string_number == string][simulation_data.dom_number == dom]["charge"].sum()

      if (data_number_of_hits > 0) and (simulation_number_of_hits > 0):
        k.append(data_number_of_hits)
        k_mc.append(simulation_number_of_hits)
        weights.append(1.0 * flasher_scaling / simulation_scaling)

  if len(k_mc) > 10:
    return poisson_equal_weights(np.asarray(k), np.asarray(k_mc), np.asarray(weights))
  else:
    return -np.inf


import flasher_data

def calculate_for_sim(simulation_data, simulation_scaling):
  return calculate_for_data_and_sim(flasher_data.all(), simulation_data, flasher_data.scaling(), simulation_scaling)


import simulation_data

def calculate(data_dir):
  return calculate_for_sim(simulation_data.flasher_hits(data_dir), simulation_data.scaling(data_dir))
