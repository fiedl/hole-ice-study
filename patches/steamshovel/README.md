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
