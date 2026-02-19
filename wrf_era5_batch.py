import sys
import os
import subprocess
import numpy as np
from datetime import datetime, timedelta

def replace_str(fileToSearch, textToSearch, textToReplace):
    with open(fileToSearch, 'r') as f:
        filedata = f.read()
    filedata = filedata.replace(textToSearch, textToReplace)
    with open(fileToSearch, 'w') as f:
        f.write(filedata)

def main():
    # Args: initdate(YYYYMMDDHH) maxfcst(H) freq(H) hash
    if len(sys.argv) < 5:
        print("Usage: python wrf_era5_batch.py <initdate> <maxfcst> <freq> <hash> [data_dir]")
        sys.exit(1)

    initdate = sys.argv[1]
    maxfcst = sys.argv[2]
    freq = sys.argv[3] # Not heavily used for ERA-5 setup but needed for compat
    run_hash = sys.argv[4]

    # Resolve package directory (set by wrf_driver_era5.sh; fall back to script location)
    package_dir = os.environ.get('ERA5_PACKAGE_DIR',
                                  os.path.dirname(os.path.abspath(__file__)))

    # Validate symlinks
    wps_exe = os.path.join(package_dir, 'wps') + '/'
    wrftemplate_dir = os.path.join(package_dir, 'wrf')
    scripts_dir = package_dir + '/'
    geo_em_file = os.environ.get('GEO_EM_FILE', '')

    for label, path in [('wrf symlink', wrftemplate_dir), ('wps symlink', wps_exe.rstrip('/'))]:
        if not os.path.exists(path):
            print(f"ERROR: {label} not found at {path}")
            print("       Run 'bash setup.sh' first to configure WRF/WPS paths.")
            sys.exit(1)

    if not geo_em_file or not os.path.exists(geo_em_file):
        print(f"ERROR: GEO_EM_FILE is not set or does not exist: '{geo_em_file}'")
        print("       Run 'bash setup.sh' to configure the domain file path.")
        sys.exit(1)

    # Get USER from environment
    user = os.environ.get('USER', 'snesbitt')
    work_base = f"/data/scratch/a/{user}/wrf_runs"
    
    # Optional data_dir if passed, otherwise assume default location
    data_dir = sys.argv[5] if len(sys.argv) > 5 else f"{work_base}/data/era5/{initdate}"
    
    print(f"Initializing ERA-5 Run: {initdate}, {maxfcst}h")
    print(f"Work base: {work_base}")

    starttime = datetime.strptime(initdate, '%Y%m%d%H')
    endtime = starttime + timedelta(hours=int(maxfcst))

    st_wps = starttime.strftime('%Y-%m-%d_%H:%M:%S')
    et_wps = endtime.strftime('%Y-%m-%d_%H:%M:%S')

    styr = starttime.strftime('%Y')
    stmo = starttime.strftime('%m')
    stdy = starttime.strftime('%d')
    sthr = starttime.strftime('%H')

    edyr = endtime.strftime('%Y')
    edmo = endtime.strftime('%m')
    eddy = endtime.strftime('%d')
    edhr = endtime.strftime('%H')

    # Directory Setup
    wps_base = os.path.join(work_base, 'domains')
    wps_dir = os.path.join(wps_base, f"{initdate}-{run_hash}")
    
    if not os.path.exists(wps_dir):
        os.makedirs(wps_dir)
        
    wrf_base = os.path.join(work_base, 'test')
    wrfrun_dir = os.path.join(wrf_base, f"{initdate}-{run_hash}")
    
    # Prep WRF Run Directory
    os.makedirs(wrf_base, exist_ok=True)
    if os.path.exists(wrfrun_dir):
        subprocess.call(f"rm -rf {wrfrun_dir}", shell=True)
    subprocess.call(f"cp -R {wrftemplate_dir} {wrfrun_dir}", shell=True)

    # WPS Setup
    os.chdir(wps_dir)
    print(f"Working in {wps_dir}")
    print(f"WPS exe dir : {wps_exe}")
    print(f"WRF template: {wrftemplate_dir}")
    print(f"Geo-em file : {geo_em_file}")

    # Symlinks to WPS executables and support files
    subprocess.call(f"ln -sf {wps_exe}link_grib.csh .", shell=True)
    subprocess.call(f"ln -sf {wps_exe}geogrid.exe .", shell=True)
    subprocess.call(f"ln -sf {wps_exe}ungrib.exe .", shell=True)
    subprocess.call(f"ln -sf {wps_exe}metgrid.exe .", shell=True)
    subprocess.call(f"ln -sf {wps_exe}ungrib/Variable_Tables/Vtable.ECMWF ./Vtable", shell=True)
    # metgrid needs ./metgrid/METGRID.TBL and geogrid needs ./geogrid/GEOGRID.TBL
    subprocess.call(f"ln -sf {wps_exe}metgrid .", shell=True)
    subprocess.call(f"ln -sf {wps_exe}geogrid .", shell=True)
    subprocess.call(f"ln -sf {geo_em_file} .", shell=True)

    # Namelist WPS
    subprocess.call(f"cp {scripts_dir}namelist.wps.template ./namelist.wps", shell=True)
    
    replace_str('namelist.wps', 'STARTDATE', st_wps)
    replace_str('namelist.wps', 'ENDDATE', et_wps)
    replace_str('namelist.wps', 'INC', str(3600)) # ERA5 is hourly

    # Link GRIB data
    # The GRIB files are in data_dir (set by get_era5_data.py)
    # Expected format: era5_sfc_*.grib and era5_pl_*.grib
    # link_grib.csh needs them.
    cmd = f"./link_grib.csh {data_dir}/era5_*"
    print(f"Running: {cmd}")
    subprocess.call(cmd, shell=True)

    # Run Ungrib
    print("Running ungrib.exe...")
    # It takes a while, so usually run in a batch job or if small enough, interactive. 
    # The original script does it here, so we will too.
    with open("ungrib.log", "w") as log:
        subprocess.call("./ungrib.exe", stdout=log, stderr=log)

    # Run Metgrid
    print("Running metgrid.exe...")
    with open("metgrid.log", "w") as log:
        subprocess.call("./metgrid.exe", stdout=log, stderr=log)

    # Link met_em files to WRF directory
    subprocess.call(f"ln -sf {wps_dir}/met_em* {wrfrun_dir}/", shell=True)

    # WRF Namelist Setup
    os.chdir(wrfrun_dir)
    subprocess.call(f"cp {scripts_dir}namelist.input.template namelist.input", shell=True)

    replace_str('namelist.input', 'STYR', styr)
    replace_str('namelist.input', 'STMO', stmo)
    replace_str('namelist.input', 'STDY', stdy)
    replace_str('namelist.input', 'STHR', sthr)

    replace_str('namelist.input', 'EDYR', edyr)
    replace_str('namelist.input', 'EDMO', edmo)
    replace_str('namelist.input', 'EDDY', eddy)
    replace_str('namelist.input', 'EDHR', edhr)

    # ERA5 has 38 (or 137 model levels, but pressure levels are usually 37/38)
    # We downloaded specific pressure levels.
    replace_str('namelist.input', 'NLEV', '38') # ERA5 PL data produces 38 metgrid levels
    
    replace_str('namelist.input', 'MODNAME', 'ERA5')
    replace_str('namelist.input', 'INC', str(3600))

    subprocess.call(f"cp {scripts_dir}variables.config .", shell=True)

    print("WPS and WRF Setup Complete.")

if __name__ == "__main__":
    main()
