import json

with open('/data/scratch/a/snesbitt/era5_wrf_package/plot_wrf_era5.ipynb', 'r') as f:
    data = json.load(f)

for cell in data['cells']:
    if cell['cell_type'] == 'code' and len(cell['source']) > 0:
        if cell['source'][0].startswith('%matplotlib widget'):
            cell['source'][0] = "get_ipython().run_line_magic('matplotlib', 'widget')\n"

with open('/data/scratch/a/snesbitt/era5_wrf_package/plot_wrf_era5.ipynb', 'w') as f:
    json.dump(data, f, indent=1)

print("Notebook patched.")
