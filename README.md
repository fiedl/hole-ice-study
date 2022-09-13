# Hole Ice Study

This project aims to incorporate the effects of [hole ice](https://wiki.icecube.wisc.edu/index.php/Hole_ice) into the [clsim](http://github.com/claudiok/clsim) photon propagation simulation of the [icecube](http://icecube.wisc.edu) neutrino observatory.

Hole ice is the ice in the refrozen columns around the detector module strings. Because its properties may differ from the properties of the surrounding ice, photon propagation simulation needs to reflect the changed properties by allowing different photon scattering and absorption behaviour within the hole ice.

The same mechanism can be used to incorporate other objects into the simulation, for example [cables](https://github.com/fiedl/hole-ice-study/issues/35).

However, the new simulation code comes at a price regarding [simulation performance](https://github.com/fiedl/hole-ice-study/issues/18): When simulating objects with small scattering length, the photons need to be scattered much more often, which increases simulation time considerably.

You may use the [hole-ice version of clsim](http://github.com/fiedl/clsim) for other studies, but be aware of the limitations as [a number of issues need to be resolved](https://github.com/fiedl/hole-ice-study/issues), yet. For example, [ice tilt and ice anisotropy are still missing](https://github.com/fiedl/hole-ice-study/issues/48).

## Results

The results of this study have been published in:

### [**The Effect of Hole Ice on the Propagation and Detection of Light in IceCube**](https://arxiv.org/abs/1904.08422) ([arxiv](https://arxiv.org/abs/1904.08422) | [pdf](https://github.com/fiedl/hole-ice-latex/releases/download/v1.0/diplomarbeit.pdf) | [latex](https://github.com/fiedl/hole-ice-latex))

2018-09-05

> IceCube is a neutrino observatory at Earth's South Pole that uses glacial ice as detector medium where particles from neutrino interactions produce light as they move through the ice, which then is detected by an array of photo detectors deployed within the ice.
>
> Aiming to improve detector calibration and thereby the observatory's precision, this study introduces methods to simulate the propagation of light through the hole ice, which is the refrozen water in the drill holes that were needed to deploy the detector modules, adding several more calibration parameters to ice models.
>
> The validity of the method is supported by unit tests, a series of cross checks, and by comparing simulation results to results gained from other studies.
>
> As examples of application, this study implements the simulation of one or several hole-ice cylinders with different properties such as position, size, scattering length, and absorption length, the simulation of shadowing cables, and a calibration method using IceCube's light-emitting diode flasher calibration system.
>
> Whereas light propagating through the bulk ice is largely unaffected, the detector modules and the flasher system located within the hole ice are effectively shielded, because a fraction of the light is absorbed and another fraction reflected by the hole ice. For detector modules displaced within the hole ice, the magnitude of this effect depends on the azimuthal direction, which is in agreement with calibration data.
>
> Simulating a light-absorbing cable next to the detector modules instead of a hole-ice cylinder can account for some of the observed effects, but not all of them, making a hole ice different from the bulk ice necessary to explain calibration data.
>
> Hole-ice effects on the detection of light by IceCube's detector modules can be approximated using modified angular-acceptance criteria for the simulated detector modules.
>
> For studies involving events with many photons and many different detector modules such as high-energy muon-track signature events, this approximation method is suitable, especially when considering simulation performance. The approximations currently in use correspond to simulated hole-ice cylinders of about 30cm diameter and about 1m effective scattering length. To account for the effect of hole-ice models suggested by current studies, however, new approximation curves are required to replace the ones currently in use.
>
> For events with less photon statistics involving only few detector modules, the direct hole-ice propagation simulation can reduce systematic uncertainties, which, however, need to be quantified by follow-up studies.

### Talks

- [ECAP Call 2019-04-04](https://github.com/fiedl/hole-ice-talk/releases/download/v1.6.1/2019-04-04.State.of.the.hole-ice.simulation.-.Erlangen-Munster.Call.-.Fiedlschuster.pdf)
- [Aachen DPG Conference 2019-03-25](https://github.com/fiedl/hole-ice-talk/releases/download/v1.7/2019-03-25.Simulation.of.Light.Propagation.Through.Hole.Ice.for.the.IceCube.Experiment.-.Fiedlschuster.-.DPG.Aachen.pdf)
- [Stockholm Collaboration Meeting 2018-09-26](https://github.com/fiedl/hole-ice-talk/releases/download/v1.2/2018-09-26.Hole-ice.simulation.in.clsim.Fiedlschuster.pdf)
- [Calibration Call 2018-03-02](https://github.com/fiedl/hole-ice-talk/releases/download/v1.0/2018-03-02.Hole-ice.simulation.in.clsim.Fiedlschuster.pdf)
- See also: [https://github.com/fiedl/hole-ice-talk/releases](https://github.com/fiedl/hole-ice-talk/releases)

### YouTube

- [Steamshovel event display of photon simulation with hole ice](https://www.youtube.com/watch?v=Wiu8CpVQn14&feature=youtu.be)


## Usage

This code has been tested against [icecube-simulation V05-00-07](http://code.icecube.wisc.edu/svn/meta-projects/simulation/releases/V05-00-07/). Until the hole-ice code has been merged into the [main clsim repository](https://github.com/claudiok/clsim), a [patched version of clsim](https://github.com/fiedl/clsim) is required. See section [Installation](#installation) on this page.

### How to activate hole-ice simulation

In order to configure clsim to simulate photon propagation through hole ice, deactivate the hole-ice approximation via angular acceptance (`UseHoleIceParameterization`) and activate hole-ice simulation (`SimulateHoleIce`) instead:

```python
tray.AddSegment(clsim.I3CLSimMakeHits,
  # ...
  UnWeightedPhotons = True,
  DOMOversizeFactor = 1.0,
  UnshadowedFraction = 1.0,
  UseHoleIceParameterization = False,
  ExtraArgumentsToI3CLSimModule = dict(
    # ...
    SimulateHoleIce = True
  )
)
```

For a working example, see [scripts/lib/propagate_photons_with_clsim.py](scripts/lib/propagate_photons_with_clsim.py).

### How to configure the hole-ice properties

The hole-ice cylinders are configured in the I3 geometry frame rather than in a separate configuration file, because the event viewer [steamshovel](https://wiki.icecube.wisc.edu/index.php/Steamshovel) can read out the geometry frame and display the hole-ice cylinders. See also section [Install steamshovel artist](#install-steamshovel-artist) below.

In order to add hole-ice cylinders to the geometry frame, add the following keys:

```python
cylinder_position = dataclasses.I3Position(
    -256.02301025390625, -521.281982421875, 0)
cylinder_radius = 0.3 # metres
cylinder_effective_scattering_length = 0.1 # metres
cylinder_absorption_length = 100.0 # metres

cylinder_scattering_length = (1.0 - 0.94) *
    cylinder_effective_scattering_length

cylinder_positions = dataclasses.I3VectorI3Position(
    [cylinder_position])
cylinder_radii = dataclasses.I3VectorFloat(
    [cylinder_radius])

cylinder_scattering_lengths = dataclasses.I3VectorFloat(
    [cylinder_scattering_length])
cylinder_absorption_lengths = dataclasses.I3VectorI3Position(
    [cylinder_absorption_length])

geometry_frame.Put("HoleIceCylinderPositions",
    cylinder_positions)
geometry_frame.Put("HoleIceCylinderRadii",
    cylinder_radii)
geometry_frame.Put("HoleIceCylinderScatteringLengths",
    cylinder_scattering_lengths)
geometry_frame.Put("HoleIceCylinderAbsorptionLengths",
    cylinder_absorption_lengths)
```

Please make sure to write the geometric scattering length to the geometry frame, not the [effective scattering length](https://wiki.icecube.wisc.edu/index.php/Effective_scattering_length). See also: [https://github.com/fiedl/hole-ice-study/issues/52](https://github.com/fiedl/hole-ice-study/issues/52)

For a working example, see [scripts/lib/create_gcd_file_with_bubble_columns_and_cables.py](scripts/lib/create_gcd_file_with_bubble_columns_and_cables.py) or [scripts/lib/create_gcd_file_with_hole_ice.py](scripts/lib/create_gcd_file_with_hole_ice.py).

## How does it work?

In photon propagation simulation, one simulation step consists of everything between two scatterings, i.e. randomizing the distance to the next scattering point, randomizing the scattering angle, moving the photon to the next scattering point, checking for absorption and checking for detection at a DOM.

<img width="500" src="https://user-images.githubusercontent.com/1679688/36198584-4339cfbe-1177-11e8-81b1-5188ff6be2e4.png" />

The following flow chart shows where the hole-ice corrections take place within the photon-propagation algorithm.

<img alt="algorithm" width="500" src="https://user-images.githubusercontent.com/1679688/41497756-2cc33348-715c-11e8-8eda-f7b655610f50.png" />

The step "calculate new position and direction" involves propagating the photon through the different ice layers, which may have different scattering and absorption lengths. The hole-ice algorithm makes this code more general such that geometric shapes other than ice layers are supported. This way, the propagation algorithm also supports adding cylinders for cables and hole-ice columns. Other shapes can by added to the algorithm as long as one can provide a method to calculate the intersection points of the photon ray and the new shape.

## Installation

### Install icecube-simulation framework

This software requires the icecube simulation framework. I've used version icecube-simulation V05-00-07.

- [How to install icecube-simulation locally on macOS Sierra](notes/2016-11-15_Installing_IceSim_on_macOS_Sierra.md)
- [How to install icecube-simulation on the Zeuthen Computer Center](notes/2018-01-23_Installing_IceSim_in_Zeuthen.md)

### Install clsim fork

This study needs a version of clsim that does support hole ice simulations. Until these changes are made public in the svn, you need to install the this clsim fork: https://github.com:fiedl/clsim.

```bash
# Get clsim fork
git clone git@github.com:fiedl/clsim.git ~/clsim
cd ~/clsim

# Symlink it into the icesim source
cd $ICESIM_ROOT/src
rm -rf clsim
ln -s ~/clsim clsim

# Compile it
cd $ICESIM_ROOT/debug_build
make -j 6
```

### Install steamshovel artist

#### Visualizing hole ice

In order to visualize hole-ice cylinders with [steamshovel](https://wiki.icecube.wisc.edu/index.php/Steamshovel), install the corresponding [artist plugins](https://github.com/fiedl/hole-ice-study/tree/master/patches/steamshovel).

```bash
git clone https://github.com/fiedl/hole-ice-study.git ~/hole-ice-study
cd $ICESIM_ROOT/src/steamshovel/python/artists
ln -s ~/hole-ice-study/patches/steamshovel/python/artists/HoleIce.py HoleIce.py
```

See also: [patches/steamshovel](https://github.com/fiedl/hole-ice-study/tree/master/patches/steamshovel) in this repository.

#### Visualizing photons

In order to visualize photons in calibration simulations, it might be necessary to modify Steamshovel's photon-path artist.

```python
# src/steamshovel/python/artists/PhotonPaths.py

# This is the code that adds photon-path points
path.addPoint(
    timesReverse[i],
    verticesReverse[i],
    colormap.value(residualsReverse[i])  # <----- but in calibration simulations, there might be no `residualsReverse`
)

# In these cases, replace the above code with:
color = colormap.value(1.0 - 1.0 * i / (len(verticesReverse) - 1))
# or: color = colormap.value(0)
path.addPoint(
    timesReverse[i],
    verticesReverse[i],
    color
)
```

### Troubleshooting

If kernel caching is active on your gpu machine, changes to `hole_ice.c` etc. might not be taken up correctly. If you plan on making changes in these files, deactivate caching by setting the environment variable `CUDA_CACHE_DISABLE=1`. See: https://github.com/fiedl/hole-ice-study/issues/15

## Author and License

Copyright (c) 2013-2019 Sebastian Fiedlschuster
and the IceCube Collaboration http://www.icecube.wisc.edu

[MIT LICENSE](MIT-LICENSE)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
