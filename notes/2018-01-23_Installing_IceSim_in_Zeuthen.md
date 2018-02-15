# 2018-01-23 Installing IceSim in Zeuthen

These notes show how to install the icecube simulation framework with the custom clsim in Zeuthen.

## Login

```bash
# Login from outside
ssh warp-zeuthen.desy.de

# Switch to gpu machine
ssh ice-wgs-gpu
```

## Connect to Github

Create an ssh key for the account on the Zeuthen machine.

```bash
ssh-keygen -t rsa -C "your_email@example.com"
cat ~/.ssh/id_rsa.pub
```

Copy the public key to https://github.com/settings/keys.

Test it:

```bash
ssh -T git@github.com
Enter passphrase for key '~/.ssh/id_rsa':
Hi! You have successfully authenticated, but GitHub does not provide shell access.
```

## Install Ruby

The wrapper scripts of this study require a current version of ruby. Therefore install [rbenv](https://github.com/rbenv/rbenv/):

```bash
git clone https://github.com/rbenv/rbenv.git ~/.rbenv
echo 'export PATH="$HOME/.rbenv/bin:$PATH"' >> ~/.zshenv
echo 'export PATH="$HOME/.rbenv/shims:$PATH"' >> ~/.zshenv
```

Restart your shell. Next, install [ruby-build](https://github.com/rbenv/ruby-build):

```bash
mkdir -p "$(rbenv root)"/plugins
git clone https://github.com/rbenv/ruby-build.git "$(rbenv root)"/plugins/ruby-build
```

To get a list of all available ruby verions, type `rbenv install --list`. Here, I've used version 2.4.3.

```bash
rbenv install 2.4.3
rbenv global 2.4.3
rbenv rehash
gem install bundler colored
```

## Environment

There are a couple of environment variables that need to be set. When using `zsh` as a shell, this is done in `~.zshenv`.

```bash
# ~/.zshenv

# rbenv
PATH="$HOME/.rbenv/bin:$PATH"
PATH="$HOME/.rbenv/shims:$PATH"

# Where is your scratch folder?
export SCRATCH="/afs/ifh.de/group/amanda/scratch/fiedl"

# Which cvmfs environment to use
eval `/cvmfs/icecube.opensciencegrid.org/py2-v3_early_access/setup.sh`

# IceCube
# Configuration:
export ICECUBE_ROOT="$SCRATCH/software"

# If you want to use a release:
export RELEASE=V05-00-07
export ICESIM_ROOT=$ICECUBE_ROOT/icecube-simulation-$RELEASE
export ICESIM=$ICESIM_ROOT/debug_build

# # If you want to use the trunk:
# export CURRENT_TRUNK=2016-02-02
# export ICESIM_ROOT=$ICECUBE_ROOT/simulation-trunk-$CURRENT_TRUNK
# export ICESIM=$ICESIM_ROOT/debug_build

# Needed by some scripts:
export I3_PORTS=$ICECUBE_ROOT/ports
export SVN="http://code.icecube.wisc.edu/svn"
export BOOST_ROOT=/usr/local/opt/boost155
export GEANT4_CONFIG=$(which geant4-config)
export I3_SRC=$ICESIM_ROOT/src
export I3_BUILD=$ICESIM
export I3_TESTDATA=/cvmfs/icecube.opensciencegrid.org/data/i3-test-data

# Make sure to deactivate opencl kernel caching.
# See: https://github.com/fiedl/hole-ice-study/issues/15
export CUDA_CACHE_DISABLE=1
```

## Install IceSim

```bash
# Get the code from svn
mkdir -p $ICESIM_ROOT
svn co $SVN/meta-projects/simulation/releases/$RELEASE/ $ICESIM_ROOT/src

# Generate cmake configuration for a debug build for debug output
mkdir -p $ICESIM_ROOT/debug_build
cd $ICESIM_ROOT/debug_build
cmake -D CMAKE_BUILD_TYPE=Debug -D SYSTEM_PACKAGES=true -D CMAKE_BUILD_TYPE:STRING=Debug ../src

# # ... or a release build for better performance
# mkdir -p $ICESIM_ROOT/build
# cd $ICESIM_ROOT/build
# cmake -D CMAKE_BUILD_TYPE=Release -D SYSTEM_PACKAGES=true -D CMAKE_BUILD_TYPE:STRING=Release ../src

# Compile it
./env-shell.sh
make -j 6
```

## Install patched clsim

This study needs a version of clsim that does support hole ice simulations. Until these changes are made public in the svn, you need to install the this clsim fork:

```bash
# Get clsim fork
git clone git@github.com:fiedl/clsim.git $SCRATCH/clsim
cd $SCRATCH/clsim
git checkout sf/hole-ice-2017

# Symlink it into the icesim source
cd $ICESIM_ROOT/src
rm -rf clsim
ln -s $SCRATCH/clsim clsim

# Compile it
cd $ICESIM_ROOT/debug_build
make -j 6
```

## Troubleshooting

### OpenCL error: could not build the OpenCL program

I've experienced this error, which is due to an [opencl bug](http://polarnick.com/blogs/gpgpu/gpu/opencl/nvidia/2017/04/28/NVIDIA-OpenCL-bug-popcount.html).

```
ERROR (I3CLSimStepToPhotonConverterOpenCL): Build Log: ptxas application ptx input, line 16; fatal   : Parsing error near '[]': syntax error
RuntimeError: OpenCL error: could build the OpenCL program!
```

Try to run it on a different gpu. Also, it worked fine for me on the cluster (`qsub`).

### Changes in the kernel files do not appear to have any effect

When kernel caching is activated on the gpu machine and changes are made to files that are `#include`d into the gpu kernel, for example `hole_ice.c` or `intersection.c`, the changes are ignored by opencl.

Workaround by deactivating caching using an environment variable.

```bash
# Make sure to deactivate opencl kernel caching.
# See: https://github.com/fiedl/hole-ice-study/issues/15
export CUDA_CACHE_DISABLE=1
```
