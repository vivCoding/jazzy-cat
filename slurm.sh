#!/bin/bash

#SBATCH --job-name vicuna-chat
#SBATCH --gres=gpu:1
#SBATCH --partition=gorman-gpu
#SBATCH --output=stdout.log

./run.sh
