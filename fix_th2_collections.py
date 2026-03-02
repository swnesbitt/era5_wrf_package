import json

path = '/data/scratch/a/snesbitt/era5_wrf_package/plot_wrf_era5.ipynb'
with open(path, 'r') as f:
    data = json.load(f)

for cell in data.get('cells', []):
    if cell.get('cell_type') == 'code':
        source = "".join(cell.get('source', []))
        if 'def update_frame(change=None):' in source:
            old_th2_contour_clear = """    # 4. Update TH2 contours
    if _th2_contours[0] is not None:
        for c in _th2_contours[0].collections:
            c.remove()
        _th2_contours[0] = None"""

            new_th2_contour_clear = """    # 4. Update TH2 contours
    if _th2_contours[0] is not None:
        if hasattr(_th2_contours[0], 'collections'):
            for c in _th2_contours[0].collections:
                c.remove()
        else:
            _th2_contours[0].remove()
        _th2_contours[0] = None"""
            
            new_source = source.replace(old_th2_contour_clear, new_th2_contour_clear)
            
            new_lines = [line + '\n' for line in new_source.split('\n')]
            new_lines[-1] = new_lines[-1][:-1] # remove trailing newline
            cell['source'] = new_lines

with open(path, 'w') as f:
    json.dump(data, f, indent=1)

print("Restored th2 contour version compatibility block for update_frame.")
