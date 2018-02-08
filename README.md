# Hole Ice Study

This project aims to incorporate the effects of [hole ice](https://wiki.icecube.wisc.edu/index.php/Hole_ice) into the [clsim](http://github.com/claudiok/clsim) photon propagation simulation of the [icecube](http://icecube.wisc.edu) neutrino observatory.

Hole ice is the ice in the refrozen columns around the detector module strings. Because its properties may differ from the properties of the surrounding ice, photon propagation simulation needs to reflect the changed properties by allowing different photon scattering and absorption behaviour within the hole ice.

## Results

### Instant Absorption Example

When simulating photon propagation for a hole ice with zero absorption length, one can visualize instant photon absorption within the hole ice cylinder.

```bash
$ICESIM/env-shell.sh
cd $HOLE_ICE_STUDY/scripts/FiringRange
./run.rb --scattering-factor=1.0 --absorption-factor=0.0 --distance=1.0 \
    --number-of-photons=1e3 --angle=90 \
    --number-of-runs=1 --number-of-parallel-runs=1 \
    --save-photon-paths --cpu
steamshovel tmp/propagated_photons.i3
```

![instant absorption example](https://user-images.githubusercontent.com/1679688/35931789-0f3c6f46-0c36-11e8-9e05-0b692c6b093c.png)

## Usage

- Which framework version is required (or tested)?
- How to set ice properties
- How to set hole ice cylinder positions

## Installation

### Install icecube-simulation framework

This software requires the icecube simulation framework. I've used version icecube-simulation V05-00-07.

- [How to install icecube-simulation locally on macOS Sierra](notes/2016-11-15_Installing_IceSim_on_macOS_Sierra.md)
- [How to install icecube-simulation on the Zeuthen Computer Center](notes/2018-01-23_Installing_IceSim_in_Zeuthen.md)

### Install clsim fork

- Use fork until merged into icesim trunk

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
