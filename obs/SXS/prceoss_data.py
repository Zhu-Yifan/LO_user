"""
Code to process the bottle data  to pickle files.
Cruise SUCCES3 was conducted from 30 July to 10 August 2009 by Dr. Burke Hales at OSU

"""

import pandas as pd
import numpy as np
import gsw
import glob

from lo_tools import Lfun, obs_functions
Ldir = Lfun.Lstart()

# This is a dict of all the columns after the initial reading.
# We add values to a key for any variable we want to save. I looked
# at units_dict (created below) to be sure about the units.
v_dict = {
    'DOY_UTC': '',
    'cruise' : 'cruise',
    'name': 'name',
    'Lat': 'lat',
    'Lon': 'lon',
    'lon': 'lon',
    'time': 'time',
    'track_dist_km': '',
    'track_dist_coast_km': '',
    'bathy_depth_m': '',
    '# profile': '',
    '#profile': '',
    'fish_depth_m': '',
    'fish_alt_m': '',
    'pressure_dbar': 'P (dbar)',
    'T0': 'IT',
    'S0': 'SP',
    'sig0': '',
    'O2_µM': 'DO (uM)',
    'O2_uM': 'DO (uM)',
    'beamC_m^-1': '',
    'NH4_µM': 'NH4 (uM)',
    'NO3_µM': 'NO3 (uM)'
}
# bottle
source = 'SXS'
otype = 'bottle'
in_dir0 = Ldir['data'] / 'obs' / source

year = 2009

# output location
out_dir = Ldir['LOo'] / 'obs' / source / otype
Lfun.make_dir(out_dir)

def round_to_nearest(value, resolution):
    return round(value / resolution) * resolution

ys = str(year)
print('\n'+ys)
# name output files
out_fn = out_dir / (ys + '.p')
info_out_fn = out_dir / ('info_' + ys + '.p')

in_fn = in_dir0.glob(f'*{source}*.csv')
df0 = pd.DataFrame()
for file in list(in_fn)[:]:
    print(file)
    df1 = pd.DataFrame()
    df00 = pd.read_csv(file, low_memory=False)
    days = df00['DOY_UTC'].astype(int)
    decimal = df00['DOY_UTC'] - days
    df00['time'] = pd.to_datetime('2009-01-01') + pd.to_timedelta(days-1, unit='D') + pd.to_timedelta(decimal * 24, unit='h')

    for vn in v_dict.keys():
        if vn in df00.columns:
            if len(v_dict[vn]) > 0:
                df1[v_dict[vn]] = df00[vn]

    # replace negative value with zero
    df1.loc[df1['NH4 (uM)'] < 0, 'NH4 (uM)'] = 0
    df1.loc[df1['NO3 (uM)'] < 0, 'NO3 (uM)'] = 0
    # use gsw
    SP = df1.SP.to_numpy()
    IT = df1.IT.to_numpy()
    p = df1['P (dbar)'].to_numpy()
    lon = df1.lon.to_numpy()
    lat = df1.lat.to_numpy()
    # - do the conversions
    z = gsw.z_from_p(p, lat)
    SA = gsw.SA_from_SP(SP, p, lon, lat)
    CT = gsw.CT_from_t(SA, IT, p)
    # - add the results to the DataFrame
    df1['SA'] = SA
    df1['CT'] = CT
    df1['z'] = z

    """
    this dataset has much higher temporal and spatial resolution than the model
    we can round lat and lon, to upscale them onto coarser resolution 2 km
    if lat the lon are the same, then label them as same cid
    e.g., at same latitude, -125 to -125.025 is ~ 2km, this will be fine
    then bin date into 1 dbar resolution 
    """
    df1['lat'] = df1['lat'].round(2)
    # df1['lon'] = df1['lon'].round(2)
    df1 = df1[(df1['lon'] >= -124.5)]
    # 0.025 degree is around 2 km
    df1['lon'] = df1['lon'].apply(lambda x: round_to_nearest(x, 0.025))

    # assign cid based on the same lon
    unique = df1.lon.unique()
    ind = {lon: cid for cid, lon in enumerate(unique)}
    df1['cid'] = df1['lon'].map(ind)

    # now bin pressure
    max_p = df1['P (dbar)'].max()
    bins = np.arange(0, max_p + 1, 1)  # 1 dbar intervals
    # Assign each P (dbar) value to a bin
    df1['P_bin'] = np.digitize(df1['P (dbar)'], bins, right=True)
    df = df1.groupby(['cid', 'P_bin']).mean().reset_index()
    # format the time a bit
    df['time'] = pd.to_datetime(df['time'].dt.strftime('%Y-%m-%d %H:%M:%S'))
    # Add cruise
    df['cruise'] = 'SUCCES3'
    # add transect name
    df['name'] = file.stem[-5:]

    cols = ['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'z',
            'CT', 'SA', 'DO (uM)', 'NH4 (uM)',
            'NO3 (uM)']
    this_cols = [item for item in cols if item in df.columns]
    df = df[this_cols]

    print(' - processed %d casts' % (len(df.cid.unique())))
    # renumber cid
    if not df0.empty:
        casts = len(df0.cid.unique())
        # print(casts)
        df['cid'] += casts
    df0 = pd.concat([df0, df], ignore_index=False)
print(' - processed %d casts in total' % (len(df0.cid.unique())))

if len(df0) > 0:
    # Save the data
    df0.to_pickle(out_fn)
    info_df = obs_functions.make_info_df(df0)
    info_df.to_pickle(info_out_fn)

