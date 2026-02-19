#!/bin/bash

#SBATCH --job-name=wrf_era5
#SBATCH --nodes=4-4
#SBATCH --ntasks=192
#SBATCH --partition=sesempi
#SBATCH --time=6:00:00
#SBATCH --mem-per-cpu=2000
#SBATCH --mail-type=ALL
#SBATCH --mail-user=${USER}@illinois.edu
#SBATCH --output="logs/slurm-%A_era5.out"

# Args:
# 1: Start Date (YYYYMMDDHH)
# 2: Duration (Hours)
# 3: Output Directory (optional; default: ./era5/<START_DATE> relative to submit dir)

if [ "$#" -lt 2 ]; then
    echo "Usage: sbatch wrf_driver_era5.sh <YYYYMMDDHH> <DURATION_HOURS> [OUTPUT_DIR]"
    exit 1
fi

START_DATE=$1
DURATION=$2
OUTPUT_DIR=${3:-"${SLURM_SUBMIT_DIR}/era5/${START_DATE}"}

# SLURM sets SLURM_SUBMIT_DIR to the directory where sbatch was called.
# We rely on this rather than $0 because SLURM copies the script to its spool dir.
PACKAGE_DIR="${SLURM_SUBMIT_DIR}"

# Validate symlinks created by setup.sh
if [ ! -e "$PACKAGE_DIR/wrf" ]; then
    echo "ERROR: $PACKAGE_DIR/wrf symlink not found."
    echo "       Run 'bash setup.sh' first to configure WRF/WPS paths."
    exit 1
fi

if [ ! -e "$PACKAGE_DIR/wps" ]; then
    echo "ERROR: $PACKAGE_DIR/wps symlink not found."
    echo "       Run 'bash setup.sh' first to configure WRF/WPS paths."
    exit 1
fi

if [ ! -f "$PACKAGE_DIR/.wrf_config" ]; then
    echo "ERROR: $PACKAGE_DIR/.wrf_config not found."
    echo "       Run 'bash setup.sh' first to configure WRF/WPS paths."
    exit 1
fi

# Export package dir so Python scripts can find templates and symlinked executables
export ERA5_PACKAGE_DIR="$PACKAGE_DIR"

# Load GEO_EM_FILE from .wrf_config and export it
source "$PACKAGE_DIR/.wrf_config"
export GEO_EM_FILE

# Base directory for all working files
WORK_BASE="/data/scratch/a/$USER/wrf_runs"

echo "Starting ERA-5 WRF Run"
echo "Start Date: $START_DATE"
echo "Duration:   $DURATION hours"
echo "Output Dir: $OUTPUT_DIR"
echo "Package Dir: $PACKAGE_DIR"
echo "WRF Dir:    $(realpath "$PACKAGE_DIR/wrf")"
echo "WPS Dir:    $(realpath "$PACKAGE_DIR/wps")"
echo "Geo-em:     $GEO_EM_FILE"

# Environment Setup
source ~/.bashrc
module purge
module load intel/intel-tbb intel/intel-compiler-rt intel/intel-umf intel/intel-oneapi intel/intel-mpi intel/hdf5-1.14.5-intel-oneapi intel/netcdf4-4.9.2-intel-oneapi

# Activate conda for python scripts
conda activate wrf-python3.12

# Scripts live in the package directory
cd "$PACKAGE_DIR"

# 1. Download Data
DATA_DIR="${WORK_BASE}/data/era5/${START_DATE}"
echo "Downloading ERA-5 data to $DATA_DIR..."
python get_era5_data.py $START_DATE $DURATION $DATA_DIR

if [ $? -ne 0 ]; then
    echo "Data download failed!"
    exit 1
fi

# 2. Run WPS / Prep WRF
RUN_HASH="ERA5-${START_DATE}"
echo "Running WPS Batch Prep..."
python wrf_era5_batch.py $START_DATE $DURATION 1 $RUN_HASH $DATA_DIR

if [ $? -ne 0 ]; then
    echo "WPS Prep failed!"
    exit 1
fi

# 3. Run Real and WRF
WRF_RUN_DIR="${WORK_BASE}/test/${START_DATE}-${RUN_HASH}"
cd $WRF_RUN_DIR

echo "Running real.exe..."
time mpirun -np 192 ./real.exe
mv rsl.out.0000 rsl.real.0000
mv rsl.error.0000 rsl.errreal.0000

if [ ! -f wrfinput_d01 ]; then
    echo "real.exe failed! wrfinput_d01 not found."
    exit 1
fi

echo "Running wrf.exe..."
time mpirun -np 192 ./wrf.exe

# 4. Move Output
echo "Moving output to $OUTPUT_DIR..."
mkdir -p $OUTPUT_DIR
mv wrfout* $OUTPUT_DIR/
mv rsl.* $OUTPUT_DIR/

echo "Done."
