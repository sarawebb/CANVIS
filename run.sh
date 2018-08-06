#!/bin/sh
#SBATCH -N 1      # nodes requested
#SBATCH --mem=10  # memory in Mb

#SBATCH --output=CANVIS_JUNE_int.out
#SBATCH --error=CANVIS_JUNE_int.err

#SBATCH --partition=skylake
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=8G


python canvis.py   
