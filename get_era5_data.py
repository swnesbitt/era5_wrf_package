import cdsapi
import sys
import os
from datetime import datetime, timedelta

def download_era5(year, month, day, time_list, output_file, pressure_level=False):
    c = cdsapi.Client()
    
    dataset = 'reanalysis-era5-pressure-levels' if pressure_level else 'reanalysis-era5-single-levels'
    
    request = {
        'product_type': 'reanalysis',
        'format': 'grib',
        'year': year,
        'month': month,
        'day': day,
        'time': time_list,
    }

    if pressure_level:
        request.update({
            'variable': [
                'geopotential', 'relative_humidity', 'temperature',
                'u_component_of_wind', 'v_component_of_wind',
            ],
            'pressure_level': [
                '1', '2', '3',
                '5', '7', '10',
                '20', '30', '50',
                '70', '100', '125',
                '150', '175', '200',
                '225', '250', '300',
                '350', '400', '450',
                '500', '550', '600',
                '650', '700', '750',
                '775', '800', '825',
                '850', '875', '900',
                '925', '950', '975',
                '1000',
            ],
        })
    else:
        request.update({
             'variable': [
                '10m_u_component_of_wind', '10m_v_component_of_wind', '2m_dewpoint_temperature',
                '2m_temperature', 'mean_sea_level_pressure', 'sea_ice_cover',
                'sea_surface_temperature', 'skin_temperature', 'soil_temperature_level_1',
                'soil_temperature_level_2', 'soil_temperature_level_3', 'soil_temperature_level_4',
                'surface_pressure', 'volumetric_soil_water_layer_1', 'volumetric_soil_water_layer_2',
                'volumetric_soil_water_layer_3', 'volumetric_soil_water_layer_4',
                 'snow_depth',
            ],
        })

    if not os.path.exists(output_file):
        print(f"Downloading {output_file}...")
        c.retrieve(dataset, request, output_file)
    else:
        print(f"{output_file} already exists, skipping.")

def main():
    if len(sys.argv) < 4:
        print("Usage: python get_era5_data.py <YYYYMMDDHH> <duration_hours> <output_dir>")
        sys.exit(1)

    start_date_str = sys.argv[1]
    duration_hours = int(sys.argv[2])
    output_dir = sys.argv[3]

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    start_date = datetime.strptime(start_date_str, "%Y%m%d%H")
    # We need data from start_date to start_date + duration_hours
    # ERA5 is hourly.
    
    # Iterate through each hour and download? Or download in chunks?
    # CDS API is usually faster with chunks. Let's do it day by day or just one big request if it's small.
    # For robustness, let's loop through required times.
    
    current_time = start_date
    end_time = start_date + timedelta(hours=duration_hours)

    # Prepare lists of years, months, days, times needed.
    # Actually, CDS requests are best done by date to avoid huge requests failing.
    # Let's group by date.
    
    dates_to_times = {}
    
    while current_time <= end_time:
        date_key = current_time.strftime("%Y-%m-%d")
        if date_key not in dates_to_times:
            dates_to_times[date_key] = []
        dates_to_times[date_key].append(current_time.strftime("%H:00"))
        current_time += timedelta(hours=1)
        
    for date_str, times in dates_to_times.items():
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        year = dt.strftime("%Y")
        month = dt.strftime("%m")
        day = dt.strftime("%d")
        
        # Define output filenames
        # Format: era5_sfc_YYYYMMDD.grib, era5_pl_YYYYMMDD.grib
        # But wait, if we have multiple times, we might want to split or keep combined.
        # WPS ungrib can handle multiple times in one file.
        # Let's keep them one file per day (or chunk of times) to keep it organized.
        
        sfc_file = os.path.join(output_dir, f"era5_sfc_{year}{month}{day}.grib")
        pl_file = os.path.join(output_dir, f"era5_pl_{year}{month}{day}.grib")
        
        # Download Surface
        # Note: If times is incomplete for a day (e.g. crossing midnight), we only ask for specific times.
        try:
            download_era5(year, month, day, times, sfc_file, pressure_level=False)
            download_era5(year, month, day, times, pl_file, pressure_level=True)
        except Exception as e:
            print(f"Error downloading data for {date_str}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
