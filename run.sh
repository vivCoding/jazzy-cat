#!/bin/bash

# set up environemnt
module load cuda/11.8
export XDG_CACHE_HOME="$HOME/scratch/.cache"

# run discord bot
conda run -n playground python3 main.py