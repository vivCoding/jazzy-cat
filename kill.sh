#!/bin/bash
jobid=$(squeue -u $USER -o "%i %j" | grep vllama | awk '{print $1}')
scancel $jobid
