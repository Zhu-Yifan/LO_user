"""
Generic code to plot any mooring extraction
"""
from lo_tools import Lfun, zfun
from lo_tools import plotting_functions as pfun
from lo_tools import bgc_from_salt as bgc

import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

Ldir = Lfun.Lstart()

verbose = False


# choose the obs file
in_dir0 = Ldir['LOo'] / 'obs'
source = Lfun.choose_item(in_dir0, tag='', exclude_tag='', itext='** Choose source from list **')
in_dir = in_dir0 / source / 'moor'
# you can choose either a file or a directory
moor_name = Lfun.choose_item(in_dir, itext='** Choose mooring observation or folder from list **')
moor_item = in_dir / moor_name
if moor_item.is_file() and moor_name[-3:]=='.nc':
    moor_fn = moor_item
elif moor_item.is_dir():
    moor_name = Lfun.choose_item(moor_item, tag='.nc', itext='** Choose mooring extraction from list **')
    moor_fn = moor_item / moor_name

obs = xr.open_dataset(moor_fn)


# choose the extraction file
in_dir0 = Ldir['LOo'] / 'extract'
gtagex = Lfun.choose_item(in_dir0, tag='', exclude_tag='', itext='** Choose gtagex from list **')
in_dir = in_dir0 / gtagex / 'moor'
# you can choose either a file or a directory
moor_name = Lfun.choose_item(in_dir, itext='** Choose mooring extraction or folder from list **')
moor_item = in_dir / moor_name
if moor_item.is_file() and moor_name[-3:]=='.nc':
    moor_fn = moor_item
elif moor_item.is_dir():
    moor_name = Lfun.choose_item(moor_item, tag='.nc', itext='** Choose mooring extraction from list **')
    moor_fn = moor_item / moor_name

# load everything using xarray
ds = xr.open_dataset(moor_fn)
ot = ds.ocean_time.values
ot_dt = pd.to_datetime(ot)
t = (ot_dt - ot_dt[0]).total_seconds().to_numpy()
T = t/86400 # time in days from start
print('time step of mooring'.center(60,'-'))
print(t[1])
print('time limits'.center(60,'-'))
print('start ' + str(ot_dt[0]))
print('end   ' + str(ot_dt[-1]))
print('info'.center(60,'-'))
VN_list = []
for vn in ds.data_vars:
    if verbose:
        print('%s %s' % (vn, ds[vn].shape))
    VN_list.append(vn)
    
# populate lists of variables to plot

vn3_list = []
if 'salt' in VN_list:
    vn3_list += ['salt', 'temp','oxygen']    
# if 'NO3' in VN_list:
#     vn3_list += ['TIC','alkalinity','oxygen','NO3']
# if 'u' in VN_list:
#     vn3_list += ['u', 'v']

# drop missing variables

vn3_list = [item for item in vn3_list if item in ds.data_vars]

# plot time series using a pandas DataFrame
df = pd.DataFrame(index=ot)
# for vn in vn2_list:
#     df[vn] = ds[vn].values
for vn in vn3_list:
    nz = 0 # 0 for bottom, -1 for top
    # df[vn] = ds[vn][:, nz] # arbitrary level
    # df[vn] = zfun.lowpass(ds[vn][:, -1].values, f='godin') # top
    df[vn] = zfun.lowpass(ds[vn][:, nz].values, f='godin') # bottom   


# output directory
    
outdir0 = Ldir['LOo'] / 'plots'/ 'moor'  
outname = 'plot_' + gtagex + '_'+ moor_name + '.png' 
print(outname)

outfile = outdir0 / outname

in_dict = dict()
in_dict['fn_out'] = outfile

plt.close('all')

pfun.start_plot(figsize=(12,8))
fig = plt.figure()
# df.plot(subplots=True, grid=True, fig=fig, title=moor_fn.name)

ylims= [(5,15),(26,34),(0,350)]

ylabels = [   'temp $(^{\circ}C)$',
              'salinity $(g\ kg^{-1})$',
              'DO $(\mu mol\ L^{-1})$'
              ]
             
ax = fig.add_subplot(311)
df.plot(y='temp',ax=ax, color = 'black',linewidth=2,label = 'Modeled')
ax.plot(obs['time'].values, obs['PT'].values, color = 'cyan',linewidth=2, label = 'Observed')
ax.set_xlim(pd.Timestamp(df.index[0]), pd.Timestamp(df.index[-1]))
ax.set_ylim(ylims[0])
ax.set_ylabel(ylabels[0])
ax.legend(loc='upper left')
ax.grid(True)
z = np.mean(ds.z_rho[:,nz].values)
ax.set_title('%s, z = %0.1f m' % (moor_name[0:5],z))

ax = fig.add_subplot(312)
df.plot(y='salt',ax=ax,color = 'black',linewidth=2,label = 'Modeled')
ax.plot(obs['time'].values, obs['SP'].values, color = 'cyan',linewidth=2, label = 'Observed')
ax.set_xlim(pd.Timestamp(df.index[0]), pd.Timestamp(df.index[-1]))
ax.set_ylim(ylims[1])
ax.set_ylabel(ylabels[1])
ax.grid(True)
ax.legend(loc='upper left')

ax = fig.add_subplot(313)
df.plot(y='oxygen',ax=ax, color = 'black',linewidth=2,label = 'Modeled')
ax.axhline(y=64, color='gray', linewidth=1, linestyle='--', label='')
ax.plot(obs['time'].values, obs['DO (uM)'].values, color = 'cyan',linewidth=2, label = 'Observed')
ax.set_xlim(pd.Timestamp(df.index[0]), pd.Timestamp(df.index[-1]))
ax.set_ylim(ylims[-1])
ax.set_ylabel(ylabels[-1])
ax.grid(True)
ax.legend(loc='upper left')


if False:
    # also make a map - could be spiffier
    fig2 = plt.figure(figsize=(8,8))
    ax2 = fig2.add_subplot()
    gfn = Ldir['data'] / 'grids' / 'cas7' / 'grid.nc'
    gds = xr.open_dataset(gfn)
    x = gds.lon_rho.values
    y = gds.lat_rho.values
    h = gds.h.values
    m = gds.mask_rho.values
    h[m==0] = np.nan
    px, py = pfun.get_plon_plat(x,y)
    mx = float(ds.lon_rho.values)
    my = float(ds.lat_rho.values)
    cs = ax2.pcolormesh(px,py,h,cmap='jet')
    fig2.colorbar(cs,ax=ax2)
    ax2.contour(x,y,h,40,colors='w')
    pfun.add_coast(ax2)
    pad = .5
    ax2.axis([mx-pad, mx+pad, my-pad, my+pad])
    pfun.dar(ax2)
    ax2.plot(mx,my,'*y')
    
plt.tight_layout()  
 
if len(str(in_dict['fn_out'])) > 0:
    plt.savefig(in_dict['fn_out'])   
    
plt.show()
pfun.end_plot()