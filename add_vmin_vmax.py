import json

path = '/data/scratch/a/snesbitt/era5_wrf_package/plot_wrf_era5.ipynb'
with open(path, 'r') as f:
    data = json.load(f)

for cell in data.get('cells', []):
    if cell.get('cell_type') == 'code':
        source = "".join(cell.get('source', []))
        if 'def update_frame(change=None):' in source:
            # We found the animation cell
            
            # Widgets
            new_source = source.replace(
                "check_topo = widgets.Checkbox(value=True, description='Topography', indent=False, layout=widgets.Layout(width='120px'))\n\ncontrols_hbox1 = widgets.HBox([play, slider, ts_label])\ncontrols_hbox2 = widgets.HBox([check_refl, check_th2, check_th2_mesh, check_barbs, check_topo, stride_box])",
                "check_topo = widgets.Checkbox(value=True, description='Topography', indent=False, layout=widgets.Layout(width='120px'))\n\nth2_vmin_box = widgets.FloatText(value=290.0, description='TH2 vmin:', layout=widgets.Layout(width='150px'))\nth2_vmax_box = widgets.FloatText(value=310.0, description='TH2 vmax:', layout=widgets.Layout(width='150px'))\n\ncontrols_hbox1 = widgets.HBox([play, slider, ts_label])\ncontrols_hbox2 = widgets.HBox([check_refl, check_th2, check_th2_mesh, check_barbs, check_topo, stride_box])\ncontrols_hbox3 = widgets.HBox([th2_vmin_box, th2_vmax_box])"
            )
            
            # Update function
            update_comp = """    # 5. Update TH2 pcolormesh
    th2_mesh.set_visible(check_th2_mesh.value)
    if check_th2_mesh.value:
        th2_mesh.set_array(wrf.to_np(th2).ravel())
        th2_mesh.set_clim(vmin=th2_vmin_box.value, vmax=th2_vmax_box.value)

    ts_label.value = timestamp"""
            
            new_source = new_source.replace(
                "    # 5. Update TH2 pcolormesh\n    th2_mesh.set_visible(check_th2_mesh.value)\n    if check_th2_mesh.value:\n        th2_mesh.set_array(wrf.to_np(th2).ravel())\n\n    ts_label.value = timestamp",
                update_comp
            )
            
            # Observer
            new_source = new_source.replace(
                "stride_box.observe(lambda change: update_frame(), names='value')\n\n# Trigger initial plot",
                "stride_box.observe(lambda change: update_frame(), names='value')\nth2_vmin_box.observe(lambda change: update_frame(), names='value')\nth2_vmax_box.observe(lambda change: update_frame(), names='value')\n\n# Trigger initial plot"
            )
            
            # Display
            new_source = new_source.replace(
                "display(widgets.VBox([controls_hbox1, controls_hbox2]))",
                "display(widgets.VBox([controls_hbox1, controls_hbox2, controls_hbox3]))"
            )
            
            new_lines = [line + '\n' for line in new_source.split('\n')]
            new_lines[-1] = new_lines[-1][:-1] # remove trailing newline
            cell['source'] = new_lines

with open(path, 'w') as f:
    json.dump(data, f, indent=1)

print("Added vmin and vmax fields for th2_mesh.")
