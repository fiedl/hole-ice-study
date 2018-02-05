# FiringRange

This is a simple test for clsim: Fire photons from a given distance onto a DOM through a hole-ice cylinder and count the hits.

![Phaser Range](https://vignette.wikia.nocookie.net/memoryalpha/images/5/51/PhaserRange.jpg/revision/latest/scale-to-width-down/640?cb=20121211232121&path-prefix=en)

## Usage

```bash
cd scripts/FiringRange
bundle exec ruby run.rb
```

Or, with parameters:

```bash
cd scripts/FiringRange
bundle exec ruby run.rb --scattering-factor=0.5 --absorption-factor=0.9 --distance=1.0
```

For all options, have a look at `ruby run.rb --help`.


## Install

```bash
git clone git@github.com/fiedl/diplomarbeit
cd diplomarbeit/scripts/FiringRange
bundle install
```