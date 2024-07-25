#!/bin/bash

# set up environemnt
module load cuda/12.1
source "$HOME/scratch/venv/bin/activate"
export XDG_CACHE_HOME="$HOME/scratch/.cache"

# run discord bot
python3 main.py
