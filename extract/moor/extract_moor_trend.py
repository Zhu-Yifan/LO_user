"""
This is a script to extract trend from LO_BGC vraibles at a mooring location.

"""


import xarray as xr
import pandas as pd
import numpy as np
from cmocean import cm
import matplotlib.pyplot as plt
from scipy.stats import linregress

from lo_tools import Lfun
from lo_tools import plotting_functions as pfun
Ldir = Lfun.Lstart()

# choose the file
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

out_dir = in_dir/'trend'
# load everything using xarray
ds = xr.open_dataset(moor_fn)

ot = ds.ocean_time.values
ot_dt = pd.to_datetime(ot)

yr1 = ot_dt[0].year
yr2 = ot_dt[-1].year

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
    print('%s %s' % (vn, ds[vn].shape))
    VN_list.append(vn)

vn3_list = []
if 'salt' in VN_list:
    vn3_list += ['salt', 'temp']
if 'NO3' in VN_list:
    vn3_list += ['oxygen', 'NO3']
    
# drop missing variables
#vn2_list = [item for item in vn2_list if item in ds.data_vars]
vn3_list = [item for item in vn3_list if item in ds.data_vars]

z = ds['z_w'].values
NT, NZ = z.shape
Z = z.mean(axis=0)
Z = Z - Z[-1] # adjust top to zero
sn = moor_name.split('_')[0]


testing = False

if testing:
    vn_list = ['oxygen']

else:
    vn_list = vn3_list



# slice and re_sample
#ds = ds.sel(time= slice(t1,t2))
#depth = 100

#ds = ds.sel(depth=depth,method='nearest')

ds= ds.resample(ocean_time='1Y').mean()

for vn in vn_list:
    var = ds[vn].values
    time_numeric = np.arange(len(ds['ocean_time']))

    # Initialize arrays to store the regression results
    slope_array = np.empty(len(ds['s_rho']))
    intercept_array = np.empty(len(ds['s_rho']))
    r_value_array = np.empty(len(ds['s_rho']))
    p_value_array = np.empty(len(ds['s_rho']))
    std_err_array = np.empty(len(ds['s_rho']))    
    
    # Performing linear regression for each layer
    for i, s in enumerate(ds['s_rho'].values):
        print(i, s)
        # Linear regression for each grid point
        slope, intercept, r_value, p_value, std_err = linregress(time_numeric, var[:, i])
        # Store results in arrays
        slope_array[i] = slope
        intercept_array[i] = intercept
        r_value_array[i] = r_value
        p_value_array[i] = p_value
        std_err_array[i] = std_err

    # Convert arrays to DataArrays
    slope_da = xr.DataArray(slope_array, dims=['s_rho'], coords={'s_rho': ds['s_rho']})
    intercept_da = xr.DataArray(intercept_array, dims=['s_rho'], coords={'s_rho': ds['s_rho']})
    r_value_da = xr.DataArray(r_value_array, dims=['s_rho'], coords={'s_rho': ds['s_rho']})
    p_value_da = xr.DataArray(p_value_array, dims=['s_rho'], coords={'s_rho': ds['s_rho']})
    std_err_da = xr.DataArray(std_err_array, dims=['s_rho'], coords={'s_rho': ds['s_rho']})

    # Append new variables to ds
    ds['slope'] = slope_da
    ds['intercept'] = intercept_da
    ds['r_value'] = r_value_da
    ds['p_value'] = p_value_da
    ds['std_err'] = std_err_da

    ds.to_netcdf(f'{out_dir}/{moor_name}_yearly_avg_trend_{vn}.nc')
    
    # plot the slope profile at the mooring site

    # output directory
    
    outdir0 = Ldir['LOo'] / 'plots'/ 'moor'  
    outname = 'plot_' + 'profile'  + '_' + vn + '_' + 'trend' + '_' + moor_name + '.png' 
    print(outname)
    outfile = outdir0 / outname
    in_dict = dict()
    in_dict['fn_out'] = outfile

    plt.close('all')
    pfun.start_plot()
    fig = plt.figure(figsize = (5.5,7.5))
    
    ax = fig.add_subplot(111)
    
    cs = ax.plot(ds['slope'].values, Z[0:30], c='r', markersize=5)
    ax.plot(np.zeros(len(ds['slope'].values)),Z[0:30], c='k', markersize=3, linestyle = '--')
    # cmap=cm.haline, ,  vmin=-10, vmax=10
    # fig.colorbar(cs)
    ax.set_ylim(top=0)
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    if vn == 'oxygen' or vn == 'NO3':
        ax.set_xlabel('$(\mu mol\ L^{-1})\ yr^{-1}$', labelpad=10)
    elif vn == 'temp':
        ax.set_xlabel('$(^{\circ}C)\ yr^{-1}$', labelpad=10)
    elif vn == 'salt':
        ax.set_xlabel('$(g\ kg^{-1})\ yr^{-1}$', labelpad=10)        
    
    ax.set_ylabel('Z [m]')
    ax.set_title(f'{vn}_trend_at_{sn}_{yr1}-{yr2}')
    
    # ax.invert_yaxis()
    
    
    plt.tight_layout()
    
    if len(str(in_dict['fn_out'])) > 0:
        plt.savefig(in_dict['fn_out'])
    plt.show()
    pfun.end_plot()


