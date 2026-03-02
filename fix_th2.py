import json

path = '/data/scratch/a/snesbitt/era5_wrf_package/plot_wrf_era5.ipynb'
with open(path, 'r') as f:
    data = json.load(f)

for cell in data.get('cells', []):
    if cell.get('cell_type') == 'code':
        new_source = []
        for line in cell.get('source', []):
            if 'for c in _th2_contours[0].collections:' in line:
                new_source.append("        if hasattr(_th2_contours[0], 'collections'):\n")
                new_source.append("            for c in _th2_contours[0].collections:\n")
            elif 'c.remove()' in line and 'for c in _th2_contours[0].collections:' in cell.get('source', [])[cell.get('source', []).index(line)-1]:
                 new_source.append(line)
                 new_source.append("        else:\n")
                 new_source.append("            _th2_contours[0].remove()\n")
            else:
                new_source.append(line)
        cell['source'] = new_source

with open(path, 'w') as f:
    json.dump(data, f, indent=1)

print("th2 contours fixed.")
