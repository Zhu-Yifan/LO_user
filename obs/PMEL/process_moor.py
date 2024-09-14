"""
Code to process the NOAA PMEL surface pCO2 mooring data.

This also formats MOORING data in the LO standard as .nc file for LO_output/obs.

Performance: Takes only seconds to run

"""

import pandas as pd
import xarray as xr
import numpy as np
import gsw
from time import time as Time

from lo_tools import Lfun
Ldir = Lfun.Lstart()

testing = False

# input location
source = 'PMEL_moor'
otype = 'moor'
in_dir = Ldir['data'] / 'obs' / source
# output location
out_dir = Ldir['LOo'] / 'obs' / 'PMEL' / otype

if not testing:
    Lfun.make_dir(out_dir, clean=True)

# these are the subset of the PMEL mooring that fall into LiveOcean model domain
sn_name_dict = {
    'CAPEELIZABETH': 'CapeElizabeth',
    'CHABA': 'Chaba',
    'NH10': 'NH10',
    'CAPEARAGO': 'CapeArago',
    'DABOB': 'Dabob',
    'TWANOH': 'Twanoh'
}

sn_loc_dict = {

    'CAPEELIZABETH': [-124.731, 47.353],
    'CHABA':         [-125.958, 47.936],
    'NH10':          [-124.778, 44.904],
    'CAPEARAGO':     [-124.500, 43.320],
    'DABOB':         [-122.803, 47.803],
    'TWANOH':        [-123.008, 47.375]
}

vn_list = ['SST', 'SSS', 'pCO2_sw', 'pH_sw', 'DOXY', 'CHL']

v_dict = {
    'datetime_utc': 'time',
    'SST': 'IT',
    'SSS': 'SP',
    'pCO2_sw': 'pCO2 (uatm)',
    'pCO2_air': '',
    'xCO2_air': '',
    'pH_sw': 'pH',
    'DOXY': 'DO (umol/kg)',
    'CHL': '',
    'NTU': ''
}

tt0 = Time()
for sn in sn_name_dict.keys():
    print(sn)
    in_file = in_dir / f'{sn}.txt'
    ds0 = pd.read_csv(in_file, delimiter='\t', skiprows=range(109), parse_dates= ['datetime_utc'])
    df0 = pd.DataFrame()
    for vn in v_dict.keys():
        # print(vn)
        if len(v_dict[vn])>0:
            df0[v_dict[vn]] = ds0[vn]
    df0 = df0.dropna(axis=0, how='all')
    df0 = df0.reset_index(drop=True)

    # average the df0 to hourly, to netcdf file
    df0.set_index('time', inplace=True)
    df = df0.resample('h').mean()
    df.reset_index(inplace=True)

    year_start = df['time'].dt.year.min()
    year_end = df['time'].dt.year.max()
    out_fn = out_dir / f'{sn_name_dict[sn]}_moor_hourly_{year_start}-{year_end}.nc'

    # use gsw
    SP = df.SP.to_numpy()
    IT = df.IT.to_numpy()
    z = np.repeat(-0.5, len(df['time'])) # the bouy is 0.5 under the sea surface
    lon = np.repeat(sn_loc_dict[sn][0], len(df['time']))
    lat = np.repeat(sn_loc_dict[sn][1], len(df['time']))
    name = np.repeat(sn_name_dict[sn], len(df['time']))
    p = gsw.p_from_z(z, lat)
    SA = gsw.SA_from_SP(SP, p, lon, lat)
    CT = gsw.CT_from_t(SA, IT, p)
    PT = gsw.pt_from_t(SA, IT, p, 0)
    rho = gsw.rho(SA,CT,p)

    # - add the results to the DataFrame
    df['lon'] = lon
    df['lat'] = lat
    df['name'] = name
    df['SA'] = SA
    df['CT'] = CT
    df['PT'] = PT
    df['z'] = z
    # - do the conversions
    df['DO (uM)'] = df['DO (umol/kg)'] *  rho

    # Keep only selected columns.
    cols = ['time', 'lat', 'lon', 'name','z', 'IT', 'PT','CT', 'SP', 'SA','pCO2 (uatm)', 'pH','DO (uM)']
    this_cols = [item for item in cols if item in df.columns]
    df = df[this_cols]
    ds = xr.Dataset.from_dataframe(df)
    ds.to_netcdf(out_fn)

print('Total time = %d sec' % (int(Time()-tt0)))

