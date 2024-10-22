"""
code to combine individual .csv datafiles from QuadraBol mooring sites for 2014-2023 into hourly .nc moor file

Details about QuadraBol:

https://www.ncei.noaa.gov/data/oceans/ncei/ocads/metadata/0208638.html
"""

import glob
import pandas as pd
import xarray as xr
import numpy as np
import gsw
from time import time as Time

from lo_tools import Lfun
Ldir = Lfun.Lstart()

testing = False
# input location
source = 'QuadraBoL'
otype = 'moor'
in_dir = Ldir['data'] / 'obs' / source
# output location
out_dir = Ldir['LOo'] / 'obs' / source / otype

if not testing:
    Lfun.make_dir(out_dir, clean=True)

sn_loc_dict = {

    'QuadraBoL': [-125.222, 50.116]
}

v_dict = {
    'TSG-T (deg C)':'TSG-T',
    'TSG-S (PSS-78)':'SP',
    'SWpCO2@TSG_T (uatm)': 'SWpCO2@TSG_T',
    'SWfCO2@TSG_T (uatm)':'SWfCO2@TSG_T',
    'SBE56_T (deg C)':'SBE56_T',
    'DiverCTD9875_Pressure (standard atm pressure removed, mbar)':'CTD9875_Pressure',
    'DiverCTD8975_T (deg C)':'CTD8975_T',
    'DiverCTD8975_S (PSS-78)':'CTD8975_S',
    'DiverCTD8967_Pressure (standard atm pressure removed, mbar)':'CTD8967_pressure',
    'DiverCTD8967_T (deg C)':'CTD8967_T',
    'DiverCTD8967_S (PSS-78)':'8967_S',
    'SBE 37 T (deg C)':'SBE_37_T',
    'SBE 37 S (PSS-78)': 'SBE_37_S',
    'SST (TSG-T minus mean delta-T_':'IT',
    'SST (TSG-T minus mean delta-T)':'IT', # for after year 2021
    'SWpCO2@SST (uatm)':'pCO2',
    'SWfCO2@SST (uatm)':'fCO2',
    'TA (umol/kg; from Evans et al., 2019 relationship)':'TA (umol/kg)',
    'TCO2 (umol/kg; Waters et al constants)':'TIC (umol/kg)',
    'pH_T (total scale; Waters et al constants)':'pH',
    'Omega_arag (Waters et al constants)':'Omega_arag',
    'Omega_calc (Waters et al constants)':'Omega_calc',
    'Revelle factor (Waters et al constants)':'Revelle_factor',
    'date and time in GMT (yyyy-mm-dd hh:mm:ss)':'time',
    'Latitude (deg N)':'lat',
    'Longitude (deg E)':'lon',

}

file = f'{in_dir}/189920*.csv'
in_file = glob.glob(file)
fn_list = sorted(in_file)

tt0 = Time()
df_list = []
for fn in fn_list:
    print(fn)
    # df0 = pd.read_csv(fn, sep=',', header=6, usecols=list(v_dict.keys()))
    ds0 = pd.read_csv(fn, sep=',', header=6)
    df0 = pd.DataFrame()
    for vn in v_dict.keys():
        if vn in ds0.columns:
            # print(vn)
            df0[v_dict[vn]] = ds0[vn]
            df0 = df0.dropna(axis=0, how='all')
            df0 = df0.reset_index(drop=True)
    df_list.append(df0)
df1 = pd.concat(df_list, ignore_index=True)
# convert time from object to Datetime
df1['time'] = pd.to_datetime(df1['time'], errors='coerce')
# average the df0 to hourly, to netcdf file
df1.set_index('time', inplace=True)
df = df1.resample('h').mean()
df.reset_index(inplace=True)
# define output file
year_start = df['time'].dt.year.min()
year_end = df['time'].dt.year.max()
sn = list(sn_loc_dict.keys())[0]
out_fn = out_dir / f'{sn}_moor_hourly_{year_start}-{year_end}.nc'
# use gsw
SP = df.SP.to_numpy()
IT = df.IT.to_numpy()
z = np.repeat(-1.0, len(df['time'])) # the bouy is 1 m under the sea surface
lon = np.repeat(sn_loc_dict[sn][0], len(df['time']))
lat = np.repeat(sn_loc_dict[sn][1], len(df['time']))

name = np.repeat(sn, len(df['time']))
p = gsw.p_from_z(z, lat)
SA = gsw.SA_from_SP(SP, p, lon, lat)
CT = gsw.CT_from_t(SA, IT, p)
PT = gsw.pt_from_t(SA, IT, p, 0)
rho = gsw.rho(SA,CT,p)
# - add the results to the DataFrame
df['lon'] = lon
df['lat'] = lat
df['name'] = name
df['SA'] = SA # Absolute salinity
df['CT'] = CT # Conservative T
df['PT'] = PT # potential T
df['z'] = z
# - do the conversions for unit
df['TA'] = df['TA (umol/kg)'] *  rho
df['TIC'] = df['TIC (umol/kg)'] *  rho
# Keep only selected columns.
# cols = ['time', 'lat', 'lon', 'name','z', 'IT', 'PT','CT', 'SP', 'SA','pCO2', 'pH','TIC', 'TA']
cols = ['time', 'IT', 'PT','CT', 'SP', 'SA','pCO2', 'pH','TIC', 'TA']
this_cols = [item for item in cols if item in df.columns]
df = df[this_cols]
df.set_index('time', inplace=True)
ds = xr.Dataset.from_dataframe(df)
# Add coordinate for latitude, longitude, and depth (z)
ds = ds.assign_coords({
    'longitude': ([], sn_loc_dict[sn][0]),  # Scalar for longitude
    'latitude': ([], sn_loc_dict[sn][1]),      # Scalar for latitude
    'depth': ([], -1.0),
})
# Add global attributes to the dataset
ds.attrs['description'] = 'Hourly sea surface data at 1 m collected from a bouy off Quadra Island in Strait of Georgia'
ds.attrs['source'] = 'https://www.ncei.noaa.gov/data/oceans/ncei/ocads/metadata/0208638.html'
ds.attrs['lat (deg N)'] = '50.116'
ds.attrs['lon (deg E)'] = '-125.222'
ds.attrs['depth'] = '-1.0'
# Add attributes to specific variables
ds['IT'].attrs['units'] = 'Celsius'
ds['IT'].attrs['long_name'] = 'In situ temperature at 1 m'

ds['PT'].attrs['units'] = 'Celsius'
ds['PT'].attrs['long_name'] = 'Potential temperature at 1 m'

ds['CT'].attrs['units'] = 'Celsius'
ds['CT'].attrs['long_name'] = 'Conservative temperature at 1 m'

ds['SP'].attrs['units'] = 'PSU'
ds['SP'].attrs['long_name'] = 'Practical salinity at 1 m'

ds['SA'].attrs['units'] = 'g/kg'
ds['SA'].attrs['long_name'] = 'Absolute Salinity at 1 m'

ds['pCO2'].attrs['units'] = 'uatm'
ds['pCO2'].attrs['long_name'] = 'Surface seawater pCO2 at 1 m'

ds['TIC'].attrs['units'] = 'umol/L'
ds['TIC'].attrs['long_name'] = 'Total Inorganic Carbon at 1 m'
ds['TIC'].attrs['note'] = 'It means DIC, not directly measured'

ds['TA'].attrs['units'] = 'umol/L'
ds['TA'].attrs['long_name'] = 'Alkalinity at 1 m'
ds['TA'].attrs['note'] = 'derived from salinity, doi: 10.3389/fmars.2018.00536'

ds['pH'].attrs['long_name'] = 'Total scale pH at 1 m'
ds['pH'].attrs['note'] = 'derived from CO2SYS'
ds.to_netcdf(out_fn, mode = 'w')

print(f'Output file is {out_fn}')
print('Total time = %d sec' % (int(Time()-tt0)))