# This script is for running the simulation on the computing cluster.
# Run this with:
#
#     qsub -l gpu -l tmpdir_size=10G -l s_rt=8:00:00 -l h_rss=2G -m ae batch-job.sh
#

# Make sure to deactivate opencl kernel caching.
# See: https://github.com/fiedl/hole-ice-study/issues/15
export CUDA_CACHE_DISABLE=1

# The scripts are located here:
SCRIPTS="$SCRATCH/hole-ice-study/scripts"

# The $REMOTE directory from which the data and scripts are taken and
# where the results will be sent to.
REMOTE="$SCRATCH/hole-ice-study/scripts/ParameterScan"

# Where to put the results later.
RESULTSDESTINATION="$REMOTE/cluster-results"
mkdir -p $RESULTSDESTINATION

# Write output to log files rather than to the shell.
exec > "$TMPDIR"/stdout.log 2> "$TMPDIR"/stderr.log

# The environment that will be loaded.
LOADENV="$SCRATCH/software/icecube-simulation-V05-00-07/debug_build/env-shell.sh"

# Where to copy the output after completing the job.
ofile="$RESULTSDESTINATION/stdout.log"
errfile="$RESULTSDESTINATION/stderr.log"

# Copy logs back to $REMOTE when the script stops.
trap 'cp "$TMPDIR"/stdout.log $ofile; cp "$TMPDIR"/stderr.log $errfile' 0
trap 'echo exit 2; exit 2' USR1 USR1 XCPU

# Load environment
source /cvmfs/icecube.opensciencegrid.org/py2-v3_early_access/setup.sh

# Copy scripts to the cluster.
for folder in ParameterScan AngularAcceptance lib; do
  mkdir -p "$TMPDIR/$folder"
  cd "$SCRIPTS/$folder"
  cp *.rb *.py Gemfile* "$TMPDIR/$folder/"
done

# Execute script.
cd $TMPDIR/ParameterScan
ruby --version
bundle install
$LOADENV zsh -c "env && bundle exec ruby run.rb $*"

# Copy result files back.
cp -r results/* $RESULTSDESTINATION/