#!/bin/bash
./kill.sh

module load cuda/11.8

sbatch slurm.sh

# if [[ "$1" != "--no-output" ]]; then
#   tail -f -n +1 stdout.log
# fi
