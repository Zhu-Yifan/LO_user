"""
Code to process the OOI mooring data that Christopher Wingard at OSU shared with us as .csv files

Data were QAQC'd by Christopher Wingard including T, S, DO, NO3, pH, pCO2

The mooring data is every 3 hours, format the data into hourly to match LO standard for LO_output/obs.

Derive CO2SYS parameters including DIC, Alkalinity, and aragonite saturation state (OmA)
using empirical relationships provided from Dr. Simone Alin (NOAA):
lat/lon boundaries: 43-50 degree north,
depth boundaries: btm depth: 10-500,
CTD depth: 13-500 dbar
"""

import pandas as pd
import xarray as xr
import numpy as np
import glob
import gsw
from lo_tools import Lfun
Ldir = Lfun.Lstart()

# input location
source = 'OOI'
otype = 'moor' # introducing a new "otype" beyond ctd and bottle
in_dir = Ldir['data'] / 'obs' / source
# output location
out_dir = Ldir['LOo'] / 'obs' / source / otype

testing = False
if not testing:
    Lfun.make_dir(out_dir, clean=False)

sn_name_dict = {

    'CE01ISSM':'Coastal Endurance Array OOI_Inshore Oregon',
    'CE02SHSM':'Coastal Endurance Array OOI_Shelf Oregon',
    'CE04OSSM':'Coastal Endurance Array OOI_Offshore Oregon',
    'CE06ISSM':'Coastal Endurance Array OOI_Inshore Washington',
    'CE07SHSM':'Coastal Endurance Array OOI_Shelf Washington',
    'CE09OSSM':'Coastal Endurance Array OOI_Offshore Washington'
}

sn_loc_dict = {
    'CE01ISSM': [-124.09583, 44.65978],
    'CE02SHSM': [-124.3032, 44.63532],
    'CE04OSSM': [-124.9398, 44.36518],
    'CE06ISSM': [-124.26973, 47.13365],
    'CE07SHSM': [-124.55202, 46.98472],
    'CE09OSSM': [-124.9509, 46.85343]
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
    'sea_water_pco2': 'pCO2',
    'sea_water_ph': 'pH'

}

for sn in sn_name_dict.keys():
    print(sn)
    # in_file = glob.glob(f'{in_dir}/{sn}/{sn}-MFD*.csv') # for bottom
    # out_fn = out_dir / (sn + '_2015_2023_hourly.nc') # for bottom
    in_file = glob.glob(f'{in_dir}/{sn}/{sn}-RID*.csv') # for surface
    out_fn = out_dir / (sn + '_surface_2015_2023_hourly.nc') # for surface
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

            print(df0['time'].iloc[jj-4])
            print(df0['time'].iloc[jj-3])
            print(df0['time'].iloc[jj-2])
            print(df0['time'].iloc[jj-1])
            print(df0['time'].iloc[jj])
            print(df0['time'].iloc[jj+1])
            print(df0['time'].iloc[jj+2])
            print(df0['time'].iloc[jj+3])
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
        rho = gsw.rho(SA,CT,p)
        sigma_theta = gsw.sigma0(SA, CT)
        # - add the results to the DataFrame
        df['SA'] = SA
        df['CT'] = CT
        df['PT'] = PT
        df['z'] = df['z'] * -1

        '''
        derive CO2SYS parameters using empirical relationships that Dr. Simone Alin (NOAA) provided:
        lat/lon boundaries : 43-50 degree north
        depth boundaries : btm depth: 10-500, CTD depth: 13-500 dbar
        '''
        df['DO (umol/kg)'] = df['DO (uM)'] * 1000 / rho
        k0 =  1022.32647598887
        k1 = -0.832126322014549
        k2 = 41.6692279540178
        k3 = 5083.01492491036
        k4 = -42269.1595306816
        k5 = 110196.285

        df['DIC (umol/kg)']  = k0 + k1 * df['DO (umol/kg)'] + k2 * sigma_theta + k3* (1/IT) + k4*(1/IT)**2 + k5*(1/IT)**3

        df['TA (umol/kg)']  = np.ones_like(df['z'].astype(float))
        # low TA
        k0 =  518.600065652408
        k1 = 50.8079078145039
        k2 = 2.25400137634154
        ind = df['SP']<=33.9
        df.loc[ind,'TA (umol/kg)'] = k0 + k1 * df.loc[ind,'SP'] + k2 * df.loc[ind,'IT']
        # High TA
        k0 =  -778.538971099741
        k1 = 87.6872377510916
        k2 = 496.571581647413
        ind = df['SP']>33.9
        df.loc[ind,'TA (umol/kg)'] = k0 + k1 * df.loc[ind,'SP'] + k2 * (1/df.loc[ind,'IT'])

        # aragonite saturation state
        k0 =  0.20152121551889
        k1 = 0.00528885932988132
        k2 = -1.1129754734998
        k3 = 0.106806165406549
        k4 = -0.00294851487660249
        k5 = 0.106761641553104
        df['OmA'] = k0 + k1 * df['DO (umol/kg)'] + k2 * IT + k3 * IT**2 + k4 * IT**3 + k5 * SP

        # convert unit from umol/kg to uM
        df['DIC (uM)'] = df['DIC (umol/kg)'] * rho /1000
        df['TA (uM)'] = df['TA (umol/kg)'] * rho /1000
        # Keep only selected columns.
        cols = ['time', 'lat', 'lon', 'z', 'CT', 'IT','SA','SP', 'DO (uM)', 'DIC (uM)', 'TA (uM)', 'pCO2','pH','OmA']
        this_cols = [item for item in cols if item in df.columns]
        df = df[this_cols]

        """
        now resample '3H' to  hourly
        but NOT interpolate with mean
        """
        df.set_index('time', inplace=True)
        df1 = df.resample('h').asfreq()
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

