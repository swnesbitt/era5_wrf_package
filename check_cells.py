import json
import ast

path = '/data/scratch/a/snesbitt/era5_wrf_package/plot_wrf_era5.ipynb'
with open(path, 'r') as f:
    data = json.load(f)

for i, cell in enumerate(data.get('cells', [])):
    if cell.get('cell_type') == 'code':
        source = "".join(cell.get('source', []))
        if 'matplotlib widget' in source: # Ignore magics
            continue
        try:
            ast.parse(source)
            print(f"Cell {i} is valid.")
        except Exception as e:
            print(f"Cell {i} has error: {e}")
