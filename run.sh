#!/bin/bash

# set up environemnt
source "$HOME/scratch/venv"
export XDG_CACHE_HOME="$HOME/scratch/.cache"

# run discord bot
python3 main.py
