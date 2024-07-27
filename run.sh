#!/bin/bash

# set up environemnt
module load cuda/11.8
export XDG_CACHE_HOME="$HOME/scratch/.cache"

# hax
sbatch -A gpu \
    --job-name=vllama --partition=scholar-gpu \
    --nodes=1 --gpus-per-node=1 \
    --time=4:00:00 --delay-boot=3:59:58 \
    --output=stdout.log --error=stdout.log ./run.sh
# run discord bot
conda run -n playground python3 main.py