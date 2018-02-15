# 2016-11-15 Installing IceSim on Sierra

## Requirements

* The [Command Line Tools](https://developer.apple.com/downloads/index.action) have to be installed.
* [Homebrew](http://brew.sh/) has to be installed.
* The `python` installation provided by Mac OS should be used. It should neither be installed by homebrew nor by a binary package from python.org.
* No installation of `I3_PORTS`. (No IceCube versions of `ports` or `cmake` are needed.)
* This guide assumes the use of *zsh* as shell. For other shells, "`~/.zshrc`" and "`~/.zshenv`" have to be replaced with the file pahts appropriate to the shell in use.

## Versions

This guide was written for the following software versions. Please feel free to update it to the current versions.

* macOS Sierra Version 10.12.1
* Zsh 5.2
* Homebrew 1.1.0-21-g9a9ab92
* Python 2.7.10
* IceSim V05-00-07

## Which python?

The [icecube offline software mac installing guide](http://software.icecube.wisc.edu/offline/projects/cmake/platforms.html) explains:

> Do not try to install your own Python over the perfectly good version shipped with the base system. It is very likely to end in tears. This includes the Enthought and Anaconda distributions as well as the Python formula in homebrew; they do not play nicely with IceTray.

For using the system version and python together with homebrew, this means:

> Some Homebrew formulas have Python as a dependency, so a second Python may sneak onto your computer without your knowledge. To avoid this, install formulas that depend on python with the parameter `--build-from-source`.

## Homebrew taps

> Homebrew is probably the easiest way to install packages on OS X, and distributes the most heavy-weight dependencies (cmake, boost, and Qt) as binary packages. Most of the required formulae are in the main distribution, but you should also tap `homebrew/science` and `IceCube-SPNO/icecube`.
> ([icecube offline software mac installing guide](http://software.icecube.wisc.edu/offline/projects/cmake/platforms.html))

Thus, as the install guide said, tap these sources:

```bash
# Install homebrew
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

# Tap the sources
brew tap homebrew/science
brew tap IceCube-SPNO/icecube
```

## Packages

The following packages are needed to build icesim:

```bash
# For Icecube "offline-software"
brew install homebrew/versions/boost155 --with-python
brew link -f homebrew/versions/boost155
export BOOST_ROOT=/usr/local/opt/boost155
brew install cmake cdk gsl minuit2 libarchive qt wget doxygen
brew install homebrew/science/healpix homebrew/science/hdf5
brew install homebrew/science/root --build-from-source
brew install boost-python --build-from-source
brew install pyqt --build-from-source

# Additionally, for IceCube "simulation"
brew install multinest pal rdmc suite-sparse pal sprng2
```

And, we need some python packages:

```bash
echo 'import site; site.addsitedir("/usr/local/lib/python2.7/site-packages")' >> ${HOME}/Library/Python/2.7/lib/python/site-packages/homebrew.pth
export PATH="${HOME}/Library/Python/2.7/bin/:${PATH}" >> ${HOME}/.zshenv
easy_install --user pip
pip install --user urwid sphinx ipython qtconsole tables
pip install --user --upgrade numpy scipy matplotlib
```

## Which release?

The icecube simulation release list can be found here:
http://code.icecube.wisc.edu/svn/meta-projects/simulation/releases/

This guide uses [V05-00-07](http://code.icecube.wisc.edu/svn/meta-projects/simulation/releases/V05-00-07/).

## Which build type?

Building with `-D CMAKE_BUILD_TYPE:STRING=Release` makes a faster framework. This is the one to use when the code is ready and the results have to be produced.

When writing the code, `-D CMAKE_BUILD_TYPE:STRING=Debug` is the better choice as it allows debug output.

There's a concenient way to have both builds: Just have them in separate folders:

```
$CURRENT_RELEASE
  |-- src
  |-- debug_build
  |-- build
```

## Environment variables

To configure the version to build and the desired paths, set the following environment variables accordingly, either in the terminal or in `~/.zshenv`.

```bash
# ~/.zshenv

# Homebrew
export PATH=/usr/local/bin:$PATH
export PATH=/usr/local/sbin:$PATH

# Python
export PYTHONPATH="${HOME}/Library/Python/2.7:${PYTHONPATH}"
export PATH="${HOME}/Library/Python/2.7/bin/:${PATH}"

# IceCube
# Configuration:
export ICECUBE_ROOT="$HOME/icecube/software"

# If you want to use a release:
export RELEASE=V05-00-07
export ICESIM_ROOT=$ICECUBE_ROOT/icecube-simulation-$RELEASE
export ICESIM=$ICESIM_ROOT/debug_build

# # If you want to use the trunk:
# export CURRENT_TRUNK=2016-02-02
# export ICESIM_ROOT=$ICECUBE_ROOT/simulation-trunk-$CURRENT_TRUNK
# export ICESIM=$ICESIM_ROOT/debug_build

# Needed by some scripts:
unset I3_PORTS
export SVN="http://code.icecube.wisc.edu/svn"
export BOOST_ROOT=/usr/local/opt/boost155
export GEANT4_CONFIG=$(which geant4-config)
export I3_SRC=$ICESIM_ROOT/src
export I3_BUILD=$ICESIM
export I3_TESTDATA=$ICECUBE_ROOT/ports/test-data

# Make sure to deactivate opencl kernel caching.
# See: https://github.com/fiedl/hole-ice-study/issues/15
export CUDA_CACHE_DISABLE=1
```

## Install icecube simulation

```bash
# Download the release
mkdir -p $ICESIM_ROOT
svn co $SVN/meta-projects/simulation/releases/$RELEASE/ $ICESIM_ROOT/src

# Build the release (debug)
mkdir -p $ICESIM_ROOT/debug_build
cd $ICESIM_ROOT/debug_build
cmake -D CMAKE_BUILD_TYPE=Debug -D SYSTEM_PACKAGES=true -D CMAKE_BUILD_TYPE:STRING=Debug ../src
./env-shell.sh
make -j 2

# # Build the release
# mkdir -p $ICESIM_ROOT/build
# cd $ICESIM_ROOT/build
# cmake -D CMAKE_BUILD_TYPE=Release -D SYSTEM_PACKAGES=true -D CMAKE_BUILD_TYPE:STRING=Release ../src
# ./env-shell.sh
# make -j 2
```

If `make -j 2` raises an error at some point, try continuing using `make`. The parameter `-j 2` uses two cpu cores to compile. But this does not always work due to dependency issues.


## Install patched clsim

This study needs a version of clsim that does support hole ice simulations. Until these changes are made public in the svn, you need to install the this clsim fork:

```bash
# Get clsim fork
git clone git@github.com:fiedl/clsim.git ~/clsim
cd ~/clsim
git checkout sf/hole-ice-2017

# Symlink it into the icesim source
cd $ICESIM_ROOT/src
rm -rf clsim
ln -s ~/clsim clsim

# Compile it
cd $ICESIM_ROOT/debug_build
make -j 6
```


## Testing

### Start the icesim environment

```bash
cd $ICESIM_ROOT/debug_build
./env-shell.sh
```

### Run a clsim test script

```bash
cd $ICESIM_ROOT/src/clsim/resources/scripts/flasher/StandardCandle
./generateTestFlashesSC.py
./applyCLSimSC.py
```

### Start Steamshovel

```bash
steamshovel $ICESIM_ROOT/src/clsim/resources/scripts/flasher/StandardCandle/test_flashesSC_clsim.i3
```


## How to ...

### Restart cmake after a change

```bash
cd $ICESIM_ROOT/debug_build
rm CMakeCache.txt
cmake -D CMAKE_BUILD_TYPE=Debug -D SYSTEM_PACKAGES=true ../src
```

## Help

Currently, the best way to get help, is on the slack channel:
Signup: https://icecube-spno.slack.com/signup

## References

* http://software.icecube.wisc.edu/simulation_trunk/projects/cmake/platforms.html#osxpythonsetup
* http://software.icecube.wisc.edu/simulation_trunk/projects/cmake/platforms.html#step-by-step-instructions
* http://builds.icecube.wisc.edu
* http://software.icecube.wisc.edu/simulation_trunk/projects/cmake/installing_ports.html#do-i-need-i3ports
