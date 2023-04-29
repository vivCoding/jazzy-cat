#!/bin/bash
module load slurm

jobid=$(squeue -u $USER -o "%i %j" | grep vicuna-chat | awk '{print $1}')
scancel $jobid
