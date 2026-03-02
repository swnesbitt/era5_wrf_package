import json

path = '/data/scratch/a/snesbitt/era5_wrf_package/plot_wrf_era5.ipynb'
with open(path, 'r') as f:
    data = json.load(f)

for cell in data.get('cells', []):
    if cell.get('cell_type') == 'code':
        new_source = []
        for line in cell.get('source', []):
            if 'REFL_CMAP_MASKED.set_under("white")' in line:
                new_source.append(line.replace('"white"', '"none"'))
            elif "REFL_CMAP_MASKED.set_under('white')" in line:
                new_source.append(line.replace("'white'", "'none'"))
            else:
                new_source.append(line)
        cell['source'] = new_source

with open(path, 'w') as f:
    json.dump(data, f, indent=1)

print("transparent setup complete.")
