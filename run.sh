#!/bin/bash

# set up environemnt
source ./venv/bin/activate
export XDG_CACHE_HOME="$HOME/scratch/.cache"

# run discord bot
python3 -m discord.main
