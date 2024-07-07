"""
Code to process the OOI mooring data that Christopher Wingard at OSU shared with us as .csv files

OOI data were QAQC'd by Christopher Wingard

The mooring data is every 3 hours, format the data into hourly to match LO standard for LO_output/obs.

"""

import pandas as pd
import xarray as xr
import numpy as np
import glob
import gsw

from lo_tools import Lfun
Ldir = Lfun.Lstart()

testing = False

# input location
source = 'OOI'
otype = 'moor' # introducing a new "otype" beyond ctd and bottle
in_dir = Ldir['data'] / 'obs' / source

# output location
out_dir = Ldir['LOo'] / 'obs' / source / otype

if not testing:
    Lfun.make_dir(out_dir, clean=True)

sn_name_dict = {

    'CE01ISSM':'Coastal Endurance Array OOI_Inshore Oregon',
    'CE02SHSM':'Coastal Endurance Array OOI_Shelf Oregon',
    'CE04OSSM':'Coastal Endurance Array OOI_Offshore Oregon',
    'CE06ISSM':'Coastal Endurance Array OOI_Inshore Washington',
    'CE07SHSM':'Coastal Endurance Array OOI_Shelf Washington',
    'CE09OSSM':'Coastal Endurance Array OOI_Offshore Washington'
}

sn_loc_dict = {
    'CE01ISSM': [-124.095, 44.6598],
    'CE02SHSM': [-124.304, 44.6393],
    'CE04OSSM': [-124.956, 44.381],
    'CE06ISSM': [-124.272, 47.1336],
    'CE07SHSM': [-124.566, 46.986],
    'CE09OSSM': [-124.972, 46.8508]
}

vn_dict = {
    'Time': '',
    'time': 'time',
    'depth': 'z',
    'sea_water_pressure': 'P (dbar)',
    'sea_water_temperature': 'IT',
    'sea_water_practical_salinity': 'SP',
    'oxygen_concentration': '',
    'oxygen_concentration_corrected': 'DO (uM)',
    'sea_water_pco2': 'pco2',
    'sea_water_ph': 'pH'

}

for sn in sn_name_dict.keys():
    print(sn)
    in_file = glob.glob(f'{in_dir}/{sn}/{sn}-MFD*.csv')
    out_fn = out_dir / (sn + '_2015_2023_hourly.nc')
    if in_file:
        print(in_file[0])
        df = pd.DataFrame()
        df00 = pd.DataFrame()
        list = []
        df0 = pd.read_csv(in_file[0], header = 0, parse_dates=['Time'], sep =',')
        # the hours is not 24-hour format, fix it
        df0['time'] = pd.NaT
        df0['Date'] = df0['Time'].dt.date
        df0['Hours'] = df0['Time'].dt.time

        for ii in range(4, len(df0)-4):
            if (df0['Hours'].iloc[ii] == pd.to_datetime('12:00:00').time() and
                    df0['Hours'].iloc[ii+4] == pd.to_datetime('12:00:00').time() and
                    df0['Date'].iloc[ii-4] == df0['Date'].iloc[ii + 3] and
                    df0['Date'].iloc[ii] != df0['Date'].iloc[ii + 4]):
                list.append(ii)
        print(list)
        # correct the datetime
        for jj in list:
            df0.at[jj-4, 'time'] = pd.Timestamp.combine(df0['Date'].iloc[jj-4], pd.to_datetime('00:00:00').time())
            df0.at[jj+3, 'time'] = df0.at[jj+3, 'Time'] + pd.Timedelta(hours=12)
            df0.at[jj+2, 'time'] = df0.at[jj+2, 'Time'] + pd.Timedelta(hours=12)
            df0.at[jj+1, 'time'] = df0.at[jj+1, 'Time'] + pd.Timedelta(hours=12)

            df0.at[jj-3, 'time'] = df0['Time'].iloc[jj-3]
            df0.at[jj-2, 'time'] = df0['Time'].iloc[jj-2]
            df0.at[jj-1, 'time'] = df0['Time'].iloc[jj-1]
            df0.at[jj, 'time'] = df0['Time'].iloc[jj]

            # print(df0['time'].iloc[jj-4])
            # print(df0['time'].iloc[jj-3])
            # print(df0['time'].iloc[jj-2])
            # print(df0['time'].iloc[jj-1])
            # print(df0['time'].iloc[jj])
            # print(df0['time'].iloc[jj+1])
            # print(df0['time'].iloc[jj+2])
            # print(df0['time'].iloc[jj+3])
        # remove NaT values
        df0 = df0[df0['time'].notnull()]

        for vn in vn_dict.keys():
            if len(vn_dict[vn]) > 0:
                df00[vn_dict[vn]] = df0[vn]

        df = pd.concat([df, df00], ignore_index=True)
        # more cleaning
        df = df.dropna(axis=0, how='all')
        df = df.reset_index(drop=True)

        # (1) Create PT, CT, SA, and z
        # - pull out variables
        SP = df.SP.to_numpy()
        IT = df.IT.to_numpy()
        p = df['P (dbar)'].to_numpy()
        lon = sn_loc_dict[sn][0]
        lat = sn_loc_dict[sn][1]
        SA = gsw.SA_from_SP(SP, p, lon, lat)
        CT = gsw.CT_from_t(SA, IT, p)
        PT = gsw.pt_from_t(SA, IT, p, 0)
        # - add the results to the DataFrame
        df['SA'] = SA
        df['CT'] = CT
        df['PT'] = PT
        df['z'] = df['z'] * -1
        # Keep only selected columns.
        cols = ['time', 'lat', 'lon', 'z', 'CT', 'PT', 'SA', 'SP', 'DO (uM)', 'pco2', 'pH']
        this_cols = [item for item in cols if item in df.columns]
        df = df[this_cols]

        """
        now resample '3H' to  hourly
        but NOT interpolate with mean
        """
        df.set_index('time', inplace=True)
        df1 = df.resample('H').asfreq()
        df1.reset_index(inplace=True)

        # save to netcdf file
        name = sn
        location = sn_name_dict[sn]
        depth = np.mean(df['z']).round(1)

        ds = xr.Dataset.from_dataframe(df1.set_index('time'))
        # ds = ds.assign_coords(name=name, lat=lat, lon=lon, depth=depth)
        # ds = ds.expand_dims(['name', 'lat', 'lon', 'depth'])

        # Assign attributes
        ds.attrs['name'] = name
        ds.attrs['location'] = location
        ds.attrs['lat'] = lat
        ds.attrs['lon'] = lon
        ds.attrs['depth (m)'] = depth

        ds.to_netcdf(out_fn)
        print(out_fn)

