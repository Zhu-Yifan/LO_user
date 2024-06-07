"""
Code to process the CTD data collected at the WA coast from two projects ECHOHAB_PNW and RISE led by Dr. Babara Hickey from UW

This takes just seconds to process 2003-2006 with ~ 2000 casts in total.

"""

import pandas as pd
import numpy as np
import gsw
from time import time as Time
from lo_tools import Lfun, obs_functions
Ldir = Lfun.Lstart()
# This is a dict of all the columns after the initial reading.
# We add values to a key for any variable we want to save.
v_dict  = {

    'Cruise': 'cruise',
    'CruiseID_CTD': '',
    'station': 'name',
    'type': '',
    'date': '',
    'time': '',
    'Datetime_UTC': 'time',
    'lat': 'lat',
    'lon': 'lon',
    'depth_bot': '',
    'PRESSURE': 'P (dbar)',
    'TEMPERATURE': '',
    'TEMPERATURE2': 'IT',
    'fluorometer_raw': '',
    'Chlorophyll_A': '',
    'Attenuation': '',
    'Transmissometry': '',
    'OXYGEN_ml': 'DO (ml/L)',
    'OXYGEN_umol': '',
    'PAR_v': '',
    'PAR': '',
    'SALINITY': '',
    'SALINITY1': '',
    'SALINITY2': 'SP',
    'TEMP_POTENTIAL': '',
    'SIGMA_T': '',
    'SIGMA_THETA': '',
    'DYNAMIC_METERS': ''

}
# CTD
source = 'HABRISE'
folder_list = ['ECOHAB_PNW','RISE']
otype = 'ctd'
testing = False

if testing:
    year_list = [2003]
    folder_list = ['ECOHAB_PNW']

else:
    year_list = range(2003,2007)

# output location
out_dir = Ldir['LOo'] / 'obs' / source / otype
Lfun.make_dir(out_dir)

tt0 = Time()
for year in year_list:
    ys = str(year)
    print('\n'+ys)
    # name output files
    out_fn = out_dir / (ys + '.p')
    info_out_fn = out_dir / ('info_' + ys + '.p')
    df00 = pd.DataFrame()
    for folder in folder_list:
        print(folder)
        in_dir0 = Ldir['data'] / 'obs' / source / folder
        in_fn = in_dir0 / 'CTD_Profiles.csv'
        # print(in_dir)
        df0 = pd.read_csv(in_fn, low_memory=False)
        # in-consistent time format
        df0['time']= df0['time'].astype(str).str.zfill(6)
        df0['date'] = df0['date'].astype(str)
        # from their BCO-DMO data page https://www.bco-dmo.org/project/2094, datetime are a GMT format equivalent to UTC
        # Directly set the timezone to UTC
        df0['Datetime_UTC']= pd.to_datetime(df0['date']  + df0['time'], format= '%Y%m%d%H%M%S')
        df0[df0== 'nd'] = np.nan
        # select one year
        t = pd.DatetimeIndex(df0.date)
        df1 = df0.loc[t.year==year,:].copy()

        if len(df1['time']) > 0:
            # select and rename variables
            df = pd.DataFrame()
            for v in df1.columns:
                if v in v_dict.keys():
                    if len(v_dict[v]) > 0:
                        df[v_dict[v]] = df1[v]
            # missing data is nd
            df[df== 'nd'] = np.nan
            df['SP'] = pd.to_numeric(df['SP'], errors='coerce')
            df['IT'] = pd.to_numeric(df['IT'], errors='coerce')
            df['DO (ml/L)'] = pd.to_numeric(df['DO (ml/L)'], errors='coerce')
            # there are some funky numbers, replace with nan
            df[df['SP']<= 0] = np.nan
            df[df['IT']<= 0] = np.nan
            df[df['P (dbar)']<= 0] = np.nan
            df = df.dropna(axis=0, how='any')
            df = df[df.time.notna()] # drop rows with bad time
            df = df.reset_index(drop=True)
            SP = df.SP.to_numpy()
            IT = df.IT.to_numpy()
            p = df['P (dbar)'].to_numpy()
            lon = df.lon.to_numpy()
            lat = df.lat.to_numpy()
            # - do the conversions
            SA = gsw.SA_from_SP(SP, p, lon, lat)
            CT = gsw.CT_from_t(SA, IT, p)
            z = gsw.z_from_p(p, lat)
            # - add the results to the DataFrame
            df['SA'] = SA
            df['CT'] = CT
            df['z'] = z
            # (2) units
            df['DO (uM)'] = df['DO (ml/L)'] * 1000 / 32
            # append to df00
            if len(df['z']) != 1:
                df00 = pd.concat([df00, df], ignore_index=True)
                # df00 = pd.concat(df, ignore_index=True)
            else:
                pass
        else:
            pass

    # (3)add cid
    unique = df00.time.unique()
    ind = {time: cid for time, cid in zip(unique, range(len(unique)))}
    df00['cid'] = df00['time'].map(ind)

    # (4) retain only selected variables
    cols = ['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'z',
            'CT', 'SA', 'DO (uM)']

    this_cols = [item for item in cols if item in df00.columns]
    df00 = df00[this_cols]

    # (5) Save the data
    if len(df00) > 0:
        df00.to_pickle(out_fn)
        info_df = obs_functions.make_info_df(df00)
        info_df.to_pickle(info_out_fn)

    print(f'processed {np.max(df00.cid)} casts in year {year}')

print('Total time = %d sec' % (int(Time()-tt0)))
