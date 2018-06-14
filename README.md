# Hole Ice Study

This project aims to incorporate the effects of [hole ice](https://wiki.icecube.wisc.edu/index.php/Hole_ice) into the [clsim](http://github.com/claudiok/clsim) photon propagation simulation of the [icecube](http://icecube.wisc.edu) neutrino observatory.

Hole ice is the ice in the refrozen columns around the detector module strings. Because its properties may differ from the properties of the surrounding ice, photon propagation simulation needs to reflect the changed properties by allowing different photon scattering and absorption behaviour within the hole ice.

The same mechanism can be used to incorporate other objects into the simulation, for example [cables](https://github.com/fiedl/hole-ice-study/issues/35).

However, the new simulation code comes at a price regarding [simulation performance](https://github.com/fiedl/hole-ice-study/issues/18): When simulating objects with small scattering length, the photons need to be scattered much more often, which increases simulation time considerably.

**Attention: This simulation code is not ready for production use, yet.** There are [a number of issues to be resolved](https://github.com/fiedl/hole-ice-study/issues), yet. For example, [ice tilt and ice anisotropy are still missing](https://github.com/fiedl/hole-ice-study/issues/48).

## Results

### Instant Absorption Example

When simulating photon propagation for a hole ice with zero absorption length, one can visualize instant photon absorption within the hole ice cylinder.

Units: Metric units. Angles in degrees.

```bash
$ICESIM/env-shell.sh
cd $HOLE_ICE_STUDY/scripts/FiringRange
./run.rb \
    --hole-ice=simulation --hole-ice-radius=0.25 \
    --effective-scattering-length=20.0 \
    --absorption-length=0.0 \
    --distance=1.0 --angle=90 \
    --number-of-photons=1e3 \
    --number-of-runs=1 --number-of-parallel-runs=1 \
    --save-photon-paths --cpu
steamshovel tmp/propagated_photons.i3
```

![instant absorption example](https://user-images.githubusercontent.com/1679688/36786032-371bd6c8-1c85-11e8-817a-0ed12e35e3b1.png)

### Angular Acceptance Example

Depending on the simulated hole ice parameters, the hole ice simulation produces similar results regarding the dom angular acceptance as the [reference study](https://github.com/fiedl/hole-ice-study/issues/10).

In the following example, the hole ice scattering length is defined to be 1/10 of the scattering length outside the hole ice. The hole ice absorption length is defined to be the same as outside the hole ice. Photons are shot from a distance of 1.0m onto the dom from different angles.

```bash
$ICESIM/env-shell.sh
cd $HOLE_ICE_STUDY/scripts/AngularAcceptance
./run.rb --scattering-factor=0.1 --absorption-factor=0.1 --distance=1.0 \
    --number-of-photons=1e5 --angles=0,10,20,30,32,45,60,75,90,105,120,135,148,160,170,180 \
    --number-of-runs=2 --number-of-parallel-runs=2
open results/current/plot_with_reference.png
```

![angular acceptance example](https://user-images.githubusercontent.com/1679688/36202267-641a2b1e-1183-11e8-968b-9df82763b247.png)

### Plane Wave Example

This is the same angular acceptance simulation, but rather than having the photons start at a single point for each angle, the starting points are randomly distributed over a plane for each angle. See: [Issue #27](https://github.com/fiedl/hole-ice-study/issues/27).

```bash
$ICESIM/env-shell.sh
cd $HOLE_ICE_STUDY/scripts/AngularAcceptance
./run.rb --scattering-factor=0.1 --absorption-factor=1.0 \
    --distance=1.0 --plane-wave \
    --number-of-photons=1e5 --angles=0,10,20,30,32,45,60,75,90,105,120,135,148,160,170,180 \
    --number-of-runs=2 --number-of-parallel-runs=2
open results/current/plot_with_reference.png
```

![plot](https://user-images.githubusercontent.com/1679688/36029509-bc087af8-0da3-11e8-82ec-28b792254ca0.png)

### Asymmetry Example

This is the same simulation, but the hole-ice cylinder and the DOM are shifted against each other by 20cm, such that the DOM is no longer centered inside the hole ice. See: [Issue #8](https://github.com/fiedl/hole-ice-study/issues/8).

```bash
$ICESIM/env-shell.sh
cd $HOLE_ICE_STUDY/scripts/AngularAcceptance
./run.rb --scattering-factor=0.1 --absorption-factor=1.0 \
    --distance=1.0 --plane-wave \
    --number-of-photons=1e5 --angles=0,10,20,30,40,50,60,70,90,120,140,150,160,170,190,200,210,220,240,260,270,290,300,310,320,330,340,350 \
    --number-of-runs=2 --number-of-parallel-runs=2 \
    --cylinder-shift=0.2
open results/current/plot_with_reference.png
```

![plot](https://user-images.githubusercontent.com/1679688/36163106-a0041ce8-10e8-11e8-87af-9981b2e62cf7.png)


## Usage

- Which framework version is required (or tested)?
- How to set ice properties
- How to set hole ice cylinder positions

## How does it work?

In photon propagation simulation, one simulation step consists of everything between two scatterings, i.a. randomizing the distance to the next scattering point, randomizing the scattering angle, moving the photon to the next scattering point, checking for absorption and checking for detection at a DOM.

![image](https://user-images.githubusercontent.com/1679688/36198584-4339cfbe-1177-11e8-81b1-5188ff6be2e4.png)

Hole ice simulation adds another task to each simulation step: Calculate the portion of the photon trajectory in the step that runs through hole ice and correct the distance to the next scattering point for the changed ice properties within the hole ice.

![image](https://user-images.githubusercontent.com/1679688/36200747-f1b8378c-117d-11e8-9e3f-8c0a5e8b944e.png)

For details, please have a look at the [hole_ice.c README](https://github.com/fiedl/clsim/tree/sf/hole-ice-2017/resources/kernels/lib/hole_ice).

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
git checkout sf/hole-ice-2018

# Symlink it into the icesim source
cd $ICESIM_ROOT/src
rm -rf clsim
ln -s ~/clsim clsim

# Compile it
cd $ICESIM_ROOT/debug_build
make -j 6
```

### Install steamshovel artist

In order to visualize hole-ice cylinders with [steamshovel](https://wiki.icecube.wisc.edu/index.php/Steamshovel), install the corresponding [artist plugins](https://github.com/fiedl/hole-ice-study/tree/master/patches/steamshovel).

TODO: Install instructions

TODO: Instructions for visualizing photons

### Troubleshooting

- If kernel caching is active on your gpu machine, changes to `hole_ice.c` etc. might not be taken up correctly. If you plan on making changes in these files, deactivate caching by setting the environment variable `CUDA_CACHE_DISABLE=1`. See: https://github.com/fiedl/hole-ice-study/issues/15

## Author and License

Copyright (c) 2013-2018 Sebastian Fiedlschuster
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
