#!/bin/bash

#SBATCH --job-name vllama
#SBATCH --gres=gpu:1
#SBATCH --partition=cuda-gpu
#SBATCH --output=stdout.log

./run.sh
