#!/bin/bash
./kill.sh

sbatch slurm.sh

if [[ "$1" != "--no-output" ]]; then
  tail -f -n +1 stdout.log
fi
