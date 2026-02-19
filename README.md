# ERA-5 WRF Workflow Deployment Package

## Overview
This package contains scripts to run WRF simulations driven by ERA-5 reanalysis data.

## Contents
- `get_era5_data.py` - Download ERA-5 data from Copernicus CDS
- `wrf_era5_batch.py` - Setup WPS/WRF directories and process data
- `wrf_driver_era5.sh` - Main SLURM driver script
- `setup.sh` - One-time setup: creates `wrf/` and `wps/` symlinks
- `requirements.yaml` - Python environment specification
- `namelist.wps.template` - WPS namelist template
- `namelist.input.template` - WRF namelist template
- `variables.config` - Variable configuration
- `README.md` - This file

## Setup

Clone this repository to a directory of your choice.

```bash
cd /data/scratch/a/${USER}/
git clone https://github.com/snesbitt/era5_wrf_package.git
```

Run once before submitting any jobs:

```bash
bash setup.sh
```

This creates `wrf/` and `wps/` symlinks in the package directory and saves the
domain file path to `.wrf_config`. All three paths can be overridden:

| Variable | Default | Description |
|---|---|---|
| `WRF_DIR` | `/data/accp/a/snesbitt/wrf47/WRFV4.7.1/test/em_real` | WRF em_real run directory |
| `WPS_DIR` | `/data/accp/a/snesbitt/wrf47/WPS-4.6.0` | WPS installation directory |
| `GEO_EM_FILE` | `/data/accp/a/snesbitt/wrf/domains/sa_3km_3/geo_em.d01.nc` | Domain geo_em.d01.nc file |

Example override:
```bash
WRF_DIR=/my/wrf WPS_DIR=/my/wps GEO_EM_FILE=/my/geo_em.d01.nc bash setup.sh
```

### Prerequisites

#### CDS API
You need a Copernicus Climate Data Store (CDS) account and API key:
1. Register at https://cds.climate.copernicus.eu/
2. Create `~/.cdsapirc` with:
```
url: https://cds.climate.copernicus.eu/api/v2
key: YOUR_UID:YOUR_API_KEY
```

#### Python Environment
A dedicated Python 3.12 environment is required for compatibility with `cdsapi`.
Create and activate it using the provided `requirements.yaml`:
```bash
conda env create -f requirements.yaml
conda activate wrf-python3.12
```

Or install manually:
```bash
conda create -n wrf-python3.12 python=3.12
conda activate wrf-python3.12
pip install cdsapi numpy
```

> **Note:** The older `wrf` environment (Python 3.7) is not compatible with `cdsapi`
> due to missing `typing.Literal` support.

#### WRF/WPS Installation
Ensure WRF and WPS are compiled and the paths exist before running `setup.sh`.

## Directory Structure
All working files use `/data/scratch/a/$USER/wrf_runs/`:
```
/data/scratch/a/$USER/wrf_runs/
├── data/era5/<YYYYMMDDHH>/     # Downloaded ERA-5 GRIB files
├── domains/<YYYYMMDDHH-HASH>/  # WPS working directory
└── test/<YYYYMMDDHH-HASH>/     # WRF run directory
```

## Usage

### Basic Usage
### Basic Usage
```bash
sbatch wrf_driver_era5.sh <YYYYMMDDHH> <hours> [output_dir]
```

### Example
Run a 72-hour simulation starting Jan 1, 2024 00Z:
```bash
# Output defaults to ./era5/2024010100/ in the current directory
sbatch wrf_driver_era5.sh 2024010100 72
```

Or specify a custom output directory:
```bash
sbatch wrf_driver_era5.sh 2024010100 72 /path/to/custom/output
```

### Monitoring
```bash
# Check job status
squeue -u $USER

# Monitor progress
tail -f slurm-<JOBID>_era5.out
```

## Resource Requirements
- **Nodes**: 4 (192 cores total)
- **Memory**: 2000 MB per core
- **Time**: 24 hours (default)
- **Partition**: sesempi
- **Disk Space**: ~1-2 GB per day of ERA-5 data

## Customization

### Change Resource Allocation
Edit `wrf_driver_era5.sh` SBATCH directives:
```bash
#SBATCH --nodes=4
#SBATCH --ntasks=192
#SBATCH --time=24:00:00
```

### Change Domain
Update paths in `wrf_era5_batch.py`:
- `wrftemplate_dir` - Your WRF template directory
- `geo_em_file` - Your domain geogrid file

## Troubleshooting

### Download Issues
- Check CDS API credentials in `~/.cdsapirc`
- CDS queue can be slow (minutes to hours)
- Check `slurm-*_era5.out` for error messages

### WPS/WRF Issues
- Check `ungrib.log` and `metgrid.log` in WPS directory
- Check `rsl.real.0000` and `rsl.error.0000` in WRF directory

### Disk Space
Monitor `/data/scratch/a/$USER/wrf_runs/` and clean old runs as needed.

## Notes
- ERA-5 provides hourly data (finer than IFS 3-hourly)
- Uses same domain configuration as IFS system
- Output saved to `./era5/<YYYYMMDDHH>/` by default, or user-specified directory

## Visualization
The included Jupyter notebook `plot_wrf_era5.ipynb` provides interactive visualization of the WRF output.

### Features
- **Topography Map**: Displays the model domain terrain.
- **Reflectivity & Wind**: Select a specific time to plot composite reflectivity and 10m wind barbs.
  - *Configuration*: Set `TARGET_TIME` in Section 2 (format `YYYYMMDD HH:MM`). The notebook automatically finds the closest output file.
- **Interactive Animation**: Animates reflectivity and winds over the entire forecast duration using a slider.

### Running the Notebook
1. Ensure the `wrf-python3.12` environment is active and registered as a kernel:
   ```bash
   conda activate wrf-python3.12
   python -m ipykernel install --user --name=wrf-python3.12
   ```
2. Launch Jupyter:
   ```bash
   jupyter notebook plot_wrf_era5.ipynb
   ```
3. Set your target time in the "USER CONFIGURATION" cell and run all cells.
- Working files automatically use scratch space
