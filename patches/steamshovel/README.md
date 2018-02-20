# Steamshovel Patches

[Steamshovel](http://software.icecube.wisc.edu/documentation/projects/steamshovel/index.html) is an event viewer that allows to visualize detector and particles in 3d.

## Hole Ice

![screenshot](https://user-images.githubusercontent.com/1679688/36309924-ab95da0c-1326-11e8-9fa5-1664dfb1678d.png)

To visualize the hole ice cylinders in steamshovel, you need to install the [HoleIce.py](python/artists/HoleIce.py) artist.

```bash
# bash
git clone https://github.com/fiedl/hole-ice-study.git ~/hole-ice-study
cd $ICESIM_ROOT/src/steamshovel/python/artists
ln -s ~/hole-ice-study/patches/steamshovel/python/artists/HoleIce.py HoleIce.py
```

## DOM Size

In the original steamshovel, the DOM radius can be chosen between 0 and 10m in steps of 10cm. But the [DOM radius](https://github.com/claudiok/clsim/blob/2faabe78762065ee5ed268c8258e77cec95a97b9/private/clsim/tabulator/I3CLSimStepToTableConverter.cxx#L181) is actually 16.510cm.

In order to visualize the [cable](https://github.com/fiedl/hole-ice-study/issues/35) next to the DOM, the DOM has to be rendered with 16.5cm radius rather than 10cm or 20cm.

![cable cylinder next to a DOM with the correct size](https://user-images.githubusercontent.com/1679688/36310702-327e6960-1329-11e8-9e81-c92d9257447c.png)

Therefore, this steamshovel patch allows to set the DOM radius in steps of 1mm and defaults the DOM radius to 16.5cm.

```bash
git clone https://github.com/fiedl/hole-ice-study.git ~/hole-ice-study
cd $ICESIM_ROOT/src/steamshovel/private/shovelart/artists
patch Detector.cpp < ~/hole-ice-study/patches/steamshovel/private/shovelart/artists/Detector.cpp.patch
```
