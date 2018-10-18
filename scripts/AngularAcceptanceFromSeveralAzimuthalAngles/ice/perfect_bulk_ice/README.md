This folder contains the ice-model configuration for perfect bulk ice, i.e. no scattering and no absorption in bulk ice.

When setting the absorption length to infinity, the simulation won't stop. Thus, I'm setting the absorption length to a large value rather than to infinity.

For the configuration documentation, see http://software.icecube.wisc.edu/documentation/projects/ppc/.

2018-10-18

### `icemodel.dat`

Each row represents an ice layer. The file must contain at least two layers.

Columns in `icemodel.dat`:

- depth of the center of the ice layer
- `be(400)`
- `adust(400)`
- `delta tau`

See: "Measurement of South Pole ice transparency with the IceCube LED calibration system", 2013, http://dx.doi.org/10.1016/j.nima.2013.01.054, section 4.

### `icemodel.par`

> file with 4 parameters of the icemodel: alpha, kappa, A, B (as defined in section 4 of the SPICE paper). Each parameter is followed by its measurement uncertainty, which is ignored by the program. The older models (older than SPICE Lea or WHAM) have 6 parameters: alpha, kappa, A, B, D, E.