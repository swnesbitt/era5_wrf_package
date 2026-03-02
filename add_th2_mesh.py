import json

path = '/data/scratch/a/snesbitt/era5_wrf_package/plot_wrf_era5.ipynb'
with open(path, 'r') as f:
    data = json.load(f)

for cell in data.get('cells', []):
    if cell.get('cell_type') == 'code':
        source = "".join(cell.get('source', []))
        if 'def update_frame(change=None):' in source:
            # We found the animation cell
            
            # Initial plot component
            new_source = source.replace(
                "refl_mesh = ax.pcolormesh(wrf.to_np(lons), wrf.to_np(lats), wrf.to_np(bref0),\n                           cmap=REFL_CMAP_MASKED, norm=norm_refl,\n                           transform=ccrs.PlateCarree(), zorder=2)",
                "th2_mesh = ax.pcolormesh(wrf.to_np(lons), wrf.to_np(lats), wrf.to_np(th2_0), cmap='viridis', alpha=0.5, transform=ccrs.PlateCarree(), zorder=1)\nplt.colorbar(th2_mesh, ax=ax, label='Potential Temperature (K)', shrink=0.7)\n\nrefl_mesh = ax.pcolormesh(wrf.to_np(lons), wrf.to_np(lats), wrf.to_np(bref0),\n                           cmap=REFL_CMAP_MASKED, norm=norm_refl,\n                           transform=ccrs.PlateCarree(), zorder=2)"
            )
            
            # Widgets
            new_source = new_source.replace(
                "check_th2 = widgets.Checkbox(value=True, description='Pot. Temp.', indent=False, layout=widgets.Layout(width='120px'))",
                "check_th2 = widgets.Checkbox(value=True, description='Pot. Temp.', indent=False, layout=widgets.Layout(width='120px'))\ncheck_th2_mesh = widgets.Checkbox(value=False, description='Pot. Temp. (fill)', indent=False, layout=widgets.Layout(width='140px'))"
            )
            
            new_source = new_source.replace(
                "controls_hbox2 = widgets.HBox([check_refl, check_th2, check_barbs, check_topo, stride_box])",
                "controls_hbox2 = widgets.HBox([check_refl, check_th2, check_th2_mesh, check_barbs, check_topo, stride_box])"
            )
            
            # Update function
            update_comp = """    # 5. Update TH2 pcolormesh
    th2_mesh.set_visible(check_th2_mesh.value)
    if check_th2_mesh.value:
        th2_mesh.set_array(wrf.to_np(th2).ravel())\n\n    ts_label.value = timestamp"""
            
            new_source = new_source.replace(
                "    ts_label.value = timestamp",
                update_comp
            )
            
            # Observer
            new_source = new_source.replace(
                "check_th2.observe(lambda change: update_frame(), names='value')",
                "check_th2.observe(lambda change: update_frame(), names='value')\ncheck_th2_mesh.observe(lambda change: update_frame(), names='value')"
            )
            
            new_lines = [line + '\n' for line in new_source.split('\n')]
            new_lines[-1] = new_lines[-1][:-1] # remove trailing newline
            cell['source'] = new_lines

with open(path, 'w') as f:
    json.dump(data, f, indent=1)

print("Added th2 mesh to animation.")
