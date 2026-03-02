import json

with open('/data/scratch/a/snesbitt/era5_wrf_package/plot_wrf_era5.ipynb', 'r') as f:
    nb = json.load(f)

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        src = "".join(cell['source'])
        if "def update_frame" in src:
            cell11_idx = i

cell11_source = """%matplotlib widget

fig, ax = plt.subplots(figsize=(12, 9), subplot_kw={'projection': cart_proj})
plt.subplots_adjust(bottom=0.1)
ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

# Static elements
ax.add_feature(cfeature.BORDERS, linewidth=1.0, edgecolor='black', zorder=5)
ax.add_feature(cfeature.STATES.with_scale('10m'), linewidth=0.5, edgecolor='black', zorder=5)
ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='black', zorder=5)

_topo_contour = [ax.contour(wrf.to_np(lons), wrf.to_np(lats), wrf.to_np(ter),
            levels=[750], colors='gray', linewidths=2.5,
            transform=ccrs.PlateCarree(), zorder=4)]

# Initial plot components
fi0, ti0 = time_index[0]
cref0, u10_0, v10_0, th2_0, ts0 = get_fields(ncfiles[fi0], ti0)

refl_mesh = ax.pcolormesh(wrf.to_np(lons), wrf.to_np(lats), wrf.to_np(cref0),
                           cmap=REFL_CMAP_MASKED, norm=norm_refl,
                           transform=ccrs.PlateCarree(), zorder=2)
plt.colorbar(refl_mesh, ax=ax, label='Composite Refl. (dBZ)', shrink=0.7)

th2_mesh = ax.pcolormesh(wrf.to_np(lons), wrf.to_np(lats), wrf.to_np(th2_0),
                           cmap='coolwarm', vmin=285, vmax=335,
                           transform=ccrs.PlateCarree(), zorder=1, alpha=0.5)
th2_mesh.set_visible(False) # hidden by default
plt.colorbar(th2_mesh, ax=ax, label='Potential Temp (K)', shrink=0.7)

_barbs = [None]
_th2_contours = [None]
_th2_labels = [[]]

title = ax.set_title(f'Weather Variables\\n{ts0}', fontsize=12)

# Widgets
play = widgets.Play(value=0, min=0, max=len(time_index)-1, step=1, interval=700, description='▶')
slider = widgets.IntSlider(value=0, min=0, max=len(time_index)-1, step=1,
                            description='Step:', continuous_update=False,
                            style={'description_width': 'initial'},
                            layout=widgets.Layout(width='60%'))
ts_label = widgets.Label(value=timestamps[0])

stride_box = widgets.IntText(value=SKIP_BARB, description='Barb Stride:', layout=widgets.Layout(width='150px'))
check_refl = widgets.Checkbox(value=True, description='Reflectivity', indent=False, layout=widgets.Layout(width='120px'))
check_th2_mesh = widgets.Checkbox(value=False, description='TH2 Pcolormesh', indent=False, layout=widgets.Layout(width='150px'))
check_th2_contour = widgets.Checkbox(value=True, description='TH2 Contours', indent=False, layout=widgets.Layout(width='150px'))
check_barbs = widgets.Checkbox(value=True, description='Wind Barbs', indent=False, layout=widgets.Layout(width='120px'))
check_topo = widgets.Checkbox(value=True, description='Topography', indent=False, layout=widgets.Layout(width='120px'))

th2_vmin_box = widgets.FloatText(value=285.0, description='TH2 vmin:', layout=widgets.Layout(width='150px'))
th2_vmax_box = widgets.FloatText(value=335.0, description='TH2 vmax:', layout=widgets.Layout(width='150px'))

controls_hbox1 = widgets.HBox([play, slider, ts_label])
controls_hbox2 = widgets.HBox([check_refl, check_th2_mesh, check_th2_contour, check_barbs, check_topo])
controls_hbox3 = widgets.HBox([stride_box, th2_vmin_box, th2_vmax_box])

# Update function
def update_frame(change=None):
    step = slider.value
    fi, ti = time_index[step]
    cref, u10, v10, th2, timestamp = get_fields(ncfiles[fi], ti)
    
    # 1. Update Reflectivity
    refl_mesh.set_visible(check_refl.value)
    if check_refl.value:
        refl_mesh.set_array(wrf.to_np(cref).ravel())
        
    # 2. Update TH2 Pcolormesh
    th2_mesh.set_visible(check_th2_mesh.value)
    if check_th2_mesh.value:
        th2_mesh.set_array(wrf.to_np(th2).ravel())
        th2_mesh.set_clim(vmin=th2_vmin_box.value, vmax=th2_vmax_box.value)
        
    # 3. Update Barbs
    s = stride_box.value
    lat_b = wrf.to_np(lats)[::s, ::s]
    lon_b = wrf.to_np(lons)[::s, ::s]
    
    if _barbs[0] is not None:
        _barbs[0].remove()
        _barbs[0] = None

    if check_barbs.value and s > 0:
        _barbs[0] = ax.barbs(lon_b, lat_b,
                              wrf.to_np(u10)[::s, ::s] * 1.94384,
                              wrf.to_np(v10)[::s, ::s] * 1.94384,
                              length=5, linewidth=0.5, color='black',
                              transform=ccrs.PlateCarree(), zorder=6)
                              
    # 4. Update TH2 contours
    if _th2_contours[0] is not None:
        for c in _th2_contours[0].collections:
            c.remove()
        _th2_contours[0] = None
        
    for txt in _th2_labels[0]:
        try:
            txt.remove()
        except:
            pass
    _th2_labels[0] = []

    if check_th2_contour.value:
        vmin = th2_vmin_box.value
        vmax = th2_vmax_box.value
        if vmax <= vmin:
            vmax = vmin + 1
        levels = np.arange(np.floor(vmin), np.ceil(vmax) + 1, 1)
        cs = ax.contour(wrf.to_np(lons), wrf.to_np(lats), wrf.to_np(th2),
                        levels=levels, colors='black', linewidths=0.5,
                        transform=ccrs.PlateCarree(), zorder=3)
        _th2_contours[0] = cs
        _th2_labels[0] = ax.clabel(cs, levels=levels[::5], inline=True, fontsize=8, fmt='%d K')

    # 5. Update Topography
    if len(_topo_contour) > 0 and _topo_contour[0] is not None:
        for c in _topo_contour[0].collections:
            c.set_visible(check_topo.value)

    title.set_text(f'Weather Variables\\n{timestamp}')
    ts_label.value = timestamp
    fig.canvas.draw_idle()

widgets.jslink((play, 'value'), (slider, 'value'))
slider.observe(lambda change: update_frame(), names='value')
check_refl.observe(lambda change: update_frame(), names='value')
check_th2_mesh.observe(lambda change: update_frame(), names='value')
check_th2_contour.observe(lambda change: update_frame(), names='value')
check_barbs.observe(lambda change: update_frame(), names='value')
check_topo.observe(lambda change: update_frame(), names='value')
stride_box.observe(lambda change: update_frame(), names='value')
th2_vmin_box.observe(lambda change: update_frame(), names='value')
th2_vmax_box.observe(lambda change: update_frame(), names='value')

# Trigger initial plot to draw everything according to widgets
update_frame()

display(widgets.VBox([controls_hbox1, controls_hbox2, controls_hbox3]))
plt.show()
"""

nb['cells'][cell11_idx]['source'] = [line + '\n' for line in cell11_source.split('\n')]

with open('/data/scratch/a/snesbitt/era5_wrf_package/plot_wrf_era5.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

