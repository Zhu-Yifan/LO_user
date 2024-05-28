"""
Generic code to plot any mooring extraction, using pcolor.
"""

from lo_tools import Lfun
from lo_tools import plotting_functions as pfun

import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from cmocean import cm
import cmcrameri.cm as cmr
import datetime
import matplotlib.dates as mdates

# PREPARING FIELDS
from PyCO2SYS import CO2SYS
import gsw
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from warnings import filterwarnings
filterwarnings('ignore') # skip a warning from PyCO2SYS

Ldir = Lfun.Lstart()

# choose the file
in_dir0 = Ldir['LOo'] / 'extract'
gtagex = Lfun.choose_item(in_dir0, tag='', exclude_tag='',
    itext='** Choose gtagex from list **')
in_dir = in_dir0 / gtagex / 'moor'
moor_name = Lfun.choose_item(in_dir, tag='.nc', exclude_tag='',
    itext='** Choose mooring extraction from list **')
moor_fn = in_dir / moor_name

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
    print('%s %s' % (vn, ds[vn].shape))
    VN_list.append(vn)
    
s = ds['salt'].values
th = ds['temp'].values
ox = ds['oxygen'].values
no3 = ds['NO3'].values
nh4 = ds['NH4'].values
tic = ds['TIC'].values
alk = ds['alkalinity'].values

z = ds['z_w'].values
lat = ds['lat_rho'].values * np.ones_like(z)
lon = ds['lon_rho'].values * np.ones_like(z)
NT, NZ = z.shape
Z = z.mean(axis=0)
Z = Z - Z[-1] # adjust top to zero


# CO2SYS

Lpres = gsw.p_from_z(z[:, 1:], lat[:, 1:]) # pressure [dbar]
SA = gsw.SA_from_SP(s, Lpres, lon[:, 1:], lat[:, 1:])
CT = gsw.CT_from_pt(SA, th)
rho = gsw.rho(SA, CT, Lpres) # in situ density
Ltemp = gsw.t_from_CT(SA, CT, Lpres) # in situ temperature
# convert from umol/L to umol/kg using in situ dentity
Lalkalinity = 1000 * alk / rho
Lalkalinity[Lalkalinity < 100] = np.nan
LTIC = 1000 * tic / rho
LTIC[LTIC < 100] = np.nan
CO2dict = CO2SYS(Lalkalinity, LTIC, 1, 2, s, Ltemp, Ltemp,
            Lpres, Lpres, 50, 2, 1, 10, 1, NH3=0.0, H2S=0.0)
# PH = CO2dict['pHout']
# PH = zfun.fillit(PH.reshape((v_dict['salt'].shape)))
ARAG = CO2dict['OmegaARout']
ARAG = ARAG.reshape((s.shape))
# ARAG = ARAG[1:-1, 1:-1]
print(np.nanmax(ARAG))
print(np.nanmin(ARAG))




# coordinate arrays for plotting
TT = T.reshape((NT,1))*np.ones((1,NZ))
ZZ = Z.reshape((1,NZ))*np.ones((NT,1))

base_date_num = mdates.date2num(datetime.datetime(1993, 1, 1))

TT = TT + base_date_num 
 


# make variables at middle times, for pcolormesh
S = (s[1:,:] + s[:-1,:])/2
TH = (th[1:,:] + th[:-1,:])/2
OX = (ox[1:,:] + ox[:-1,:])/2
OX = OX*32/1000 # convert uM to mg/L
NO3 = (no3[1:,:] + no3[:-1,:])/2
NH4 = (nh4[1:,:] + nh4[:-1,:])/2
TIC = (tic[1:,:] + tic[:-1,:])/2
ALK = (alk[1:,:] + alk[:-1,:])/2
omega = (ARAG[1:,:] + ARAG[:-1,:])/2


plt.close('all')
pfun.start_plot()
fig = plt.figure(figsize = (24, 10))

ax = fig.add_subplot(321)
cs = ax.pcolormesh(TT, ZZ, S, cmap=cm.haline, vmin=28, vmax=33)
fig.colorbar(cs)
ax.set_ylim(top=0.5)
ax.set_ylabel('Z [m]')
ax.set_title(moor_name)

ax.text(.05, .1, 'Salinity $(g\ kg^{-1})$', c='k', weight='bold', transform=ax.transAxes)

ax.xaxis.set_major_locator(mdates.YearLocator())  
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  
#ax.xaxis.grid(False, which='major', color='black', linewidth=1.5)
ax.yaxis.grid(False)


ax = fig.add_subplot(322)
cs = ax.pcolormesh(TT, ZZ, TH, cmap=cm.balance, vmin=6, vmax=18)
fig.colorbar(cs)
ax.set_ylim(top=0.5)
ax.set_ylabel('Z [m]')
ax.set_title(moor_name)
ax.text(.05, .1, 'Potential Temperature $({\circ}C)$', c='k', weight='bold', transform=ax.transAxes)
ax.xaxis.set_major_locator(mdates.YearLocator())  
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  
#ax.xaxis.grid(False, which='major', color='black', linewidth=1.5)
ax.yaxis.grid(False)


ax = fig.add_subplot(323)
cs = ax.pcolormesh(TT, ZZ, OX, cmap=cm.oxy, vmin=0, vmax=10)

fig.colorbar(cs)
ax.set_ylim(top=0.5)

ax.set_ylabel('Z [m]')
ax.text(.05, .1, 'Dissolved Oxygen $(mg\ L^{-1})$', c='k', weight='bold', transform=ax.transAxes)
ax.xaxis.set_major_locator(mdates.YearLocator())  
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  
#ax.xaxis.grid(False, which='major', color='black', linewidth=1.5)
ax.yaxis.grid(False)


ax = fig.add_subplot(324)
cs = ax.pcolormesh(TT, ZZ, NH4, cmap=cmr.hawaii_r, vmin=0, vmax=10)
fig.colorbar(cs)
ax.set_ylim(top=0.5)
ax.set_ylabel('Z [m]')
ax.text(.05, .1, 'Ammonium $(\mu mol\ L^{-1})$', c='k', weight='bold', transform=ax.transAxes)
ax.xaxis.set_major_locator(mdates.YearLocator())  
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  
#ax.xaxis.grid(False, which='major', color='black', linewidth=1.5)
ax.yaxis.grid(False)


ax = fig.add_subplot(325)
cs = ax.pcolormesh(TT, ZZ, omega , cmap='coolwarm_r', vmin=0, vmax=3)
#cs = ax.pcolormesh(TT, ZZ, OX, cmap='jet', vmin=0, vmax=10)
fig.colorbar(cs)
ax.xaxis.set_major_locator(mdates.YearLocator())  
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  
#ax.xaxis.grid(False, which='major', color='black', linewidth=1.5)
ax.yaxis.grid(False)
ax.set_ylim(top=0.5)
ax.set_xlabel('\nTime (year)')
ax.set_ylabel('Z [m]')
ax.text(.05, .1, 'ARAG', c='k', weight='bold', transform=ax.transAxes)

ax = fig.add_subplot(326)
cs = ax.pcolormesh(TT, ZZ, NO3, cmap=cmr.hawaii_r, vmin=0, vmax=40)
fig.colorbar(cs)
ax.set_ylim(top=0.5)
ax.set_ylabel('Z [m]')

ax.text(.05, .1, 'Nitrate $(\mu mol\ L^{-1})$', c='k', weight='bold', transform=ax.transAxes)
ax.set_xlabel('\nTime (year)')
ax.xaxis.set_major_locator(mdates.YearLocator())  
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))  
#ax.xaxis.grid(False, which='major', color='black', linewidth=1.5)
ax.yaxis.grid(False)

# output directory
    
outdir0 = Ldir['LOo'] / 'plots'/ 'moor'  
outname = 'plot_' + 'profile'  + '_' + moor_name + '.png' 
print(outname)

outfile = outdir0 / outname

in_dict = dict()
in_dict['fn_out'] = outfile

plt.tight_layout()

# set the spacing between subplots      
plt.subplots_adjust(left=0.05,
                    bottom=0.1,
                    right=1.025,
                    top=0.96,
                    wspace=0.05,
                    hspace=0.25)

if len(str(in_dict['fn_out'])) > 0:
    plt.savefig(in_dict['fn_out'])

plt.show()

pfun.end_plot()