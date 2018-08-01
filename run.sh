#!/bin/sh
#SBATCH -N 1      # nodes requested
#SBATCH --mem=10  # memory in Mb

#SBATCH --output=CANVIS_46_10000.out
#SBATCH --error=CANVIS_46_10000.err

#SBATCH --partition=skylake
#SBATCH --time=13-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=8G


python canvis_46_10000.py   
