"""
code to process the matlab mooring dataset in Project ECOHAB_PNW
this script extracts CTD+DO at 32 m depth from mooring EH4 in 2005

"""

from scipy.io import loadmat
import pandas as pd
import xarray as xr
import numpy as np
import gsw
from time import time as Time

from lo_tools import Lfun
Ldir = Lfun.Lstart()

# input location
source = 'HABRISE'
folder = 'CTD_moor'
otype = 'moor'
in_dir = Ldir['data'] / 'obs' / source / folder

# output location
out_dir = Ldir['LOo'] / 'obs' / source / otype
Lfun.make_dir(out_dir)

v_dict = {

    'daten_hr': 'matlab_time',
    'date_hr': '',
    'o_hr': 'DO (ml/L)',
    's_hr': 'SP',
    't_hr': 'IT',
    'pr_hr': 'P (dbar)',
    'lat': '',
    'lon': '',
    'z': '',
    'wdep': ''
}
# moor_name
sn = 'E4'

sn_loc_dict = {
    'E4': [-124.5335, 47.6007]
}

year = 2005

# function to covert matlab datenum to datetime
def matlab_to_datetime(matlab_datenum):
    days = matlab_datenum - 366
    fractional_days = matlab_datenum % 1
    return datetime.fromordinal(int(days)) + timedelta(days=fractional_days)

tt0 = Time()
in_fn = in_dir / 'e405sbe_hrly_tc.mat'
moor_dict = loadmat(in_fn)
out_fn = out_dir / (sn + f'_{year}_hourly.nc')
df = pd.DataFrame()
for v in moor_dict.keys():
    if v in v_dict.keys():
        if len(v_dict[v]) > 0:
            print(v_dict[v])
            df0 = pd.DataFrame()
            df0[v_dict[v]] = pd.DataFrame(moor_dict[v])
            df = pd.concat([df, df0], axis=1)
lon = np.repeat(moor_dict['lon'], len(df['matlab_time']))
lat = np.repeat(moor_dict['lat'], len(df['matlab_time']))
z = np.repeat(moor_dict['z'], len(df['matlab_time']))
name = np.repeat(sn, len(df['matlab_time']))
SP = df.SP.to_numpy()
IT = df.IT.to_numpy()
p = df['P (dbar)'].to_numpy()
SA = gsw.SA_from_SP(SP, p, lon, lat)
CT = gsw.CT_from_t(SA, IT, p)
# get PT
PT = gsw.pt_from_t(SA, IT, p, 0)
# convert matlabtime to datetime
df['time'] = df['matlab_time'].apply(matlab_to_datetime)
# convert unit DO
df['DO (uM)'] = df['DO (ml/L)'] * 44.6596
# add moor name
df['name'] = name
df['lon'] = lon
df['lat'] = lat
df['z'] = z
df['PT'] = PT
df['CT'] = CT
df['SA'] = SA

columns= ['time', 'lat', 'lon', 'name', 'z', 'CT', 'PT','SA','SP', 'DO (uM)']
df = df[columns]

ds = xr.Dataset.from_dataframe(df)
ds.to_netcdf(out_fn)
print(out_fn)
print('Total time = %d sec' % (int(Time()-tt0)))