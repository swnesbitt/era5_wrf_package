import json

path = '/data/scratch/a/snesbitt/era5_wrf_package/plot_wrf_era5.ipynb'
with open(path, 'r') as f:
    data = json.load(f)

for cell in data.get('cells', []):
    if cell.get('cell_type') == 'code':
        new_source = []
        for line in cell.get('source', []):
            if "title = ax.set_title(f'Weather Variables" in line or "title.set_text(f'Weather Variables" in line:
                new_source.append('# ' + line)
            elif "Weather Variables" in line:
                new_source.append('# ' + line)
            else:
                new_source.append(line)
        cell['source'] = new_source

with open(path, 'w') as f:
    json.dump(data, f, indent=1)

print("Removed Weather Variables titles.")
