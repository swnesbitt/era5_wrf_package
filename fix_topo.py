import json

path = '/data/scratch/a/snesbitt/era5_wrf_package/plot_wrf_era5.ipynb'
with open(path, 'r') as f:
    data = json.load(f)

for cell in data.get('cells', []):
    if cell.get('cell_type') == 'code':
        source = "".join(cell.get('source', []))
        if 'def update_frame(change=None):' in source:
            new_source = source.replace(
                "    # 5. Update Topography\n    if len(_topo_contour) > 0 and _topo_contour[0] is not None:\n        for c in _topo_contour[0].collections:\n            c.set_visible(check_topo.value)",
                "    # 5. Update Topography\n    if len(_topo_contour) > 0 and _topo_contour[0] is not None:\n        if hasattr(_topo_contour[0], 'collections'):\n            for c in _topo_contour[0].collections:\n                c.set_visible(check_topo.value)\n        else:\n            for path_collection in _topo_contour[0].get_paths():\n                pass # not an easy visibility setting for new contour sets, let's just use .set_visible if available\n            try:\n                _topo_contour[0].set_visible(check_topo.value)\n            except:\n                pass"
            )
            
            # actually let me make it identical to the working one before
            new_source = source.replace(
                "    if len(_topo_contour) > 0 and _topo_contour[0] is not None:\n        for c in _topo_contour[0].collections:\n            c.set_visible(check_topo.value)",
                "    if len(_topo_contour) > 0 and _topo_contour[0] is not None:\n        if hasattr(_topo_contour[0], 'collections'):\n            for c in _topo_contour[0].collections:\n                c.set_visible(check_topo.value)\n        else:\n            _topo_contour[0].set_visible(check_topo.value)"
            )
            
            new_lines = [line + '\n' for line in new_source.split('\n')]
            new_lines[-1] = new_lines[-1][:-1] # remove trailing newline
            cell['source'] = new_lines

with open(path, 'w') as f:
    json.dump(data, f, indent=1)

print("Topo contour fixed.")
