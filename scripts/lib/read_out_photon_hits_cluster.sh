# See: https://github.com/fiedl/hole-ice-study/issues/57#issuecomment-383943993

# The folder to process is expected as parameter.
FOLDER=$1

# The $REMOTE directory from which the data and scripts are taken and
# where the results will be sent to.
REMOTE="$SCRATCH/hole-ice-study/scripts/lib"

# The environment that will be loaded.
LOADENV="$SCRATCH/software/icecube-simulation-V05-00-07/debug_build/env-shell.sh"

# Write output to log files rather than to the shell.
exec > "$FOLDER"/read-out-stdout.log 2> "$FOLDER"/read-out-stderr.log

# Load environment.
source /cvmfs/icecube.opensciencegrid.org/py2-v3_early_access/setup.sh

# Execute script.
cd $FOLDER
pwd
ls
$LOADENV zsh -c "$REMOTE/read_out_photon_hits.py --i3-file=$FOLDER/propagated_photons.i3 --outfile=$FOLDER/hits.txt"