#!/usr/bin/env python3

# This script simulates a shifted bubble column and creates effective
# angular-acceptance curves for plane waves of photons coming in from
# several azimuthal directions.
#
# See: https://github.com/fiedl/hole-ice-study/issues/117

bubble_column_configs = [ # all lengths in meters
  {"offset": 0.15, "radius": 0.075, "geometric_scattering_length": 0.10},
  {"offset": 0.15, "radius": 0.15, "geometric_scattering_length": 0.10},
  {"offset": 0.15, "radius": 0.15, "geometric_scattering_length": 0.70},
  {"offset": 0.15, "radius": 0.30, "geometric_scattering_length": 0.70},
]

incoming_azimuthal_angles = [0, 120, 240] # degrees

# What are the incoming polar angles?
# See: https://github.com/fiedl/hole-ice-study/issues/117#issuecomment-430986133
#
import numpy as np
delta_x = 20.0
delta_z_range = np.arange(-150, 151, 10)
incoming_polar_angles = [0] + [90 + np.arctan(1.0 * delta_z / delta_x) / np.pi * 180 for delta_z in delta_z_range] + [180]


# Check environment requirements.
import os
if not "I3_PORTS" in os.environ: raise RuntimeError("Environment variable $I3_PORTS is not set, which is needed for clsim working with geant4.")

# dom_position =