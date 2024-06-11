"""
Code to process the bottle data collected at the WA coast from two projects ECHOHAB_PNW and RISE

This takes just seconds to process 400 stations collected during 2003-2006.

"""

import pandas as pd
import numpy as np
import gsw
from time import time as Time

from lo_tools import Lfun, obs_functions
Ldir = Lfun.Lstart()

# This is a dict of all the columns after the initial reading.
# We add values to a key for any variable we want to save.
v_dict = {

    'Cruise': 'cruise',
    'CruiseID_CTD': 'cruise',
    'Station': 'name',
    'Survey': '',
    'Date': '',
    'date': '',
    'Time': '',
    'Datetime_UTC': 'time',
    'Event': '',
    'Source': '',
    'depth': '',
    'depthID': '',
    'Lat': 'lat',
    'Lon': 'lon',
    'lat': 'lat',
    'lon': 'lon',
    'PN_RelAbund': '',
    'PN_Total': '',
    'percentPN_p_m': '',
    'percentPN_a_f_h': '',
    'percentPN_pd_d': '',
    'Chl_a': '',
    'CHL': 'Chl',
    'NO3_NO2': 'NO3 (uM)',
    'N': 'NO3 (uM)',
    'SiO2': 'SiO4 (uM)',
    'Si': 'SiO4 (uM)',
    'P': 'PO4 (uM)',
    'H2PO4': 'PO4 (uM)',
    'RBA_pDA': '',
    'ELISA_pDA': '',
    'dDA': '',
    'Bacteria': '',
    'Cyanobacteria': '',
    'Fe': '',
    'bottle': '',
    'Pr': 'P (dbar)',
    'DepS': '',
    'temp1': '',
    'temp2': 'IT',
    'sal1_uncorrected': '',
    'sal2_uncorrected': 'SP',
    'sal1_corrected': '',
    'sal2_corrected': '',
    'sal2': 'SP',
    'par': '',
    'v_fl': '',
    'fls': '',
    'v_transmiss': '',
    'bat': '',
    'v_ox': '',
    'sbeox0ML_L': 'DO (ml/L)',
    'oxy_ml': 'DO (ml/L)',
    'v_par': ''

}

# CTD
source = 'HABRISE'
folder_list = ['ECOHAB_PNW','RISE']
otype = 'bottle'

testing = False
if testing:
    year_list = [2004]
    folder_list = ['ECOHAB_PNW','RISE']
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
        # read bottle data
        in_dir0 = Ldir['data'] / 'obs' / source / folder
        in_fn0 = in_dir0 / 'AllBottle.csv'
        df0 = pd.read_csv(in_fn0, low_memory=False)
        # read CTD data
        in_fn = in_dir0 / 'CTD_Profiles.csv'
        dt =  pd.read_csv(in_fn,  low_memory=False)

        if folder == 'ECOHAB_PNW':
            # there is no time column in the file, match time with ctd file
            # keep lon and lat same with df0
            dt['lon'] = dt['lon'].round(2)
            dt['lat'] = dt['lat'].round(2)
            # keep CTD as a source
            df0 = df0[df0['Source'] == 'CTD']
            # assign 'time' to df0 based on the same date, lon, lat
            dfm = pd.merge(df0, dt[['date', 'lon', 'lat', 'time']], on=['date', 'lon', 'lat'], how='left')
            df0['time'] = dfm['time']
            # if not match, drop data
            df0 = df0[pd.notna(df0['time'])]
            # keep the dtype to the same as dt
            df0['time'] = df0['time'].astype('int64')

        elif year == 2003 and folder == 'ECOHAB_PNW':
            pass

        else:
            """ 
            there is no temp, sal, and DO column in the bottle file
            it only provides depth
            we need to match them with ctd file that is 1 dbar binned 
            
            """
            z = pd.to_numeric(df0['depth'], errors='coerce')
            lat = df0.Lat.to_numpy()
            # create Pr column
            df0['Pr'] = gsw.p_from_z(-z, lat)
            # now round pressure because CTD is 1db-binned
            df0['pres'] = df0['Pr'].round(0)
            df0['date'] = df0['Date']
            df0['time'] = df0['Time']

            df0['lon'] = df0['Lon'].round(2)
            df0['lat'] = df0['Lat'].round(2)
            dt['lon'] = dt['lon'].round(2)
            dt['lat'] = dt['lat'].round(2)

            dt['pres'] = dt['PRESSURE']
            dt['temp2'] = dt['TEMPERATURE2']
            dt['sal2'] = dt['SALINITY2']
            dt['oxy_ml'] = dt['OXYGEN_ml']
            # now match
            dfm = pd.merge(df0, dt[['date', 'lon', 'lat', 'time', 'pres', 'temp2', 'sal2', 'oxy_ml']], on=['date', 'lon', 'lat','pres'], how='left')
            df0['temp2'] = dfm['temp2']
            df0['sal2'] = dfm['sal2']
            df0['oxy_ml'] = dfm['oxy_ml']


        # in-consistent time format
        df0['time'] = df0['time'].astype(str).str.zfill(6)
        df0['date'] = df0['date'].astype(str)
        # from their BCO-DMO data page https://www.bco-dmo.org/project/2094, datetime are a GMT format equivalent to UTC
        # Directly set the timezone to UTC
        df0['Datetime_UTC'] = pd.to_datetime(df0['date'] + df0['time'], format='%Y%m%d%H%M%S')

        df0[df0 == 'nd'] = np.nan
        # for each year
        t = pd.DatetimeIndex(df0.date)
        df1 = df0.loc[t.year == year, :].copy()
        if len(df1['time']) > 0:
            # select and rename variables
            df = pd.DataFrame()
            for v in df1.columns:
                if v in v_dict.keys():
                    if len(v_dict[v]) > 0:
                        df[v_dict[v]] = df1[v]

            df['SP'] = pd.to_numeric(df['SP'], errors='coerce')
            df['IT'] = pd.to_numeric(df['IT'], errors='coerce')
            df['P (dbar)'] = pd.to_numeric(df['P (dbar)'], errors='coerce')
            df['NO3 (uM)'] = pd.to_numeric(df['NO3 (uM)'], errors='coerce')
            df['PO4 (uM)'] = pd.to_numeric(df['PO4 (uM)'], errors='coerce')
            df['SiO4 (uM)'] = pd.to_numeric(df['SiO4 (uM)'], errors='coerce')
            df['DO (ml/L)'] = pd.to_numeric(df['DO (ml/L)'], errors='coerce')

            df[df['SP'] <= 0] = np.nan
            df[df['IT'] <= 0] = np.nan
            df[df['P (dbar)'] <= 0] = np.nan
            df = df.dropna(axis=0, how='any')
            # drop rows with bad time
            df = df[df.time.notna()]
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
            # convert Sea-Bird oxygen sensor data given in mL O2 (gas at S.T.P) per L of seawater
            # into µmol O2 per L of seawater
            df['DO (uM)'] = df['DO (ml/L)'] * 44.6596

            # append to df00
            if len(df['z']) != 1:
                df00= pd.concat([df00, df], ignore_index=True)
                # df00 = pd.concat(df, ignore_index=True)
            else:
                pass
        else:
            pass

    # (3) add cid
    unique = df00.time.unique()
    ind = {time: cid for time, cid in zip(unique, range(len(unique)))}
    df00['cid'] = df00['time'].map(ind)

    # (4) retain only selected variables
    cols = ['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'z',
            'CT', 'SA', 'NO3 (uM)', 'PO4 (uM)', 'SiO4 (uM)', 'DO (uM)']

    this_cols = [item for item in cols if item in df00.columns]
    df00 = df00[this_cols]

    # (5) Save the data
    if len(df00) > 0:
        df00.to_pickle(out_fn)
        info_df = obs_functions.make_info_df(df00)
        info_df.to_pickle(info_out_fn)

    print(f'processed {np.max(df00.cid)} stations in year {year}')

print('Total time = %d sec' % (int(Time()-tt0)))
