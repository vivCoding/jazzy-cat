#!/bin/bash

#SBATCH --job-name vllama
#SBATCH --gres=gpu:1
#SBATCH --partition=cuda-gpu
#SBATCH --output=stdout.log
#SBATCH --error=stdout.log

# ./run.sh

# sbatch -A gpu --nodes=1 --gres=gpu:1 -t 00:01:00 gpu_hello.sub
# sbatch -A gpu --nodes=1 --gpus-per-node=1 --time=96:00:00 ./run.sh
sbatch -A gpu \
    --job-name=vllama --partition=scholar-gpu \
    --nodes=1 --gpus-per-node=1 \
    --time=4:00:00 \
    --output=stdout.log --error=stdout.log ./run.sh