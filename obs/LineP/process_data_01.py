"""
Code to process the Line P bottle data 1990-1997.

"""

import pandas as pd
import numpy as np
import gsw
import sys

from lo_tools import Lfun, obs_functions
Ldir = Lfun.Lstart()

# BOTTLE
source = 'LineP'
otype = 'bottle'
in_dir0 = Ldir['data'] / 'obs' / source / otype

testing = True

if testing:
    year_list = [1997]
else:
    # 1990-1997 has different columns than 1998-2019
    year_list = range(1990,1998)

# output location
out_dir = Ldir['LOo'] / 'obs' / source / otype
Lfun.make_dir(out_dir)

# This is a dict of all the columns after the initial reading.
# We add values to a key for any variable we want to save. I looked
# at units_dict (created below) to be sure about the units.
v_dict = {
    'time':'time',
    'EXPOCODE':'',
    'CRUISE_ID':'cruise',
    'STATION_ID':'name',
    'EVENT_NO':'cid',
    'NISKIN_NO':'',
    'YEAR_UTC':'',
    'MONTH_UTC':'',
    'DAY_UTC':'',
    'TIME_UTC':'',
    'YEARDAY_UTC':'',
    'LONGITUDE_DEC':'lon',
    'LATITUDE_DEC':'lat',
    'CTDPRS_DBAR':'',
    'DEPTH_METER':'z',
    'CTDTMP_ITS90_DEG_C':'',
    'TMP_REVERSING_DEG_C':'IT',
    'CTDSAL_PSS78':'',
    'CTDSAL_FLAG_W':'',
    'SALINITY_PSS78':'SP',
    'SALINITY_FLAG_W':'',
    'OXYGEN_UMOL_KG':'DO (umol/kg)',
    'OXYGEN_FLAG_W':'',
    'DIC_UMOL_KG':'DIC (umol/kg)',
    'DIC_FLAG_W':'',
    'TA_UMOL_KG':'TA (umol/kg)',
    'TA_FLAG_W':'',
    'NITRATE_NITRITE_UMOL_KG':'NO3 (umol/kg)',
    'NITRATE_NITRITE_FLAG_W':'',
    'SILICATE_UMOL_KG':'SiO4 (umol/kg)',
    'SILICATE_FLAG_W':'',
    'PHOSPHATE_UMOL_KG':'PO4 (umol/kg)',
    'PHOSPHATE_FLAG_W':'',
    'original_filename':'',
}

load_data = True
for year in year_list:
    ys = str(year)
    print('\n'+ys)

    # name output files
    out_fn = out_dir / (ys + '.p')
    info_out_fn = out_dir / ('info_' + ys + '.p')

    if year in year_list:
        in_fn = in_dir0 / 'LineP_for_Data_Synthesis_1990-2019_v1.csv'
        """
        there are two rows have bad data, which is row 700, and 724, omit these 
        """
        df0 = pd.read_csv(in_fn, low_memory=False,
                          parse_dates={'time':['YEAR_UTC','MONTH_UTC','DAY_UTC','TIME_UTC']})
        df0 = df0.drop([699, 723])
        df0 = df0.reset_index(drop=True)

        load_data = False # only load the first time
        # select one year
    t = pd.DatetimeIndex(df0.time)
    df1 = df0.loc[t.year==year,:].copy()

    # select and rename variables
    df = pd.DataFrame()
    for v in df1.columns:
        if v in v_dict.keys():
            if len(v_dict[v]) > 0:
                df[v_dict[v]] = df1[v]

    # missing data is -999
    df[df==-999] = np.nan

    # a little more cleaning up
    df = df.dropna(axis=0, how='all') # drop rows with no good data
    df = df[df.time.notna()] # drop rows with bad time
    df = df.reset_index(drop=True)

    # Line P goes way beyond the model domain, now limit the geographical region to the model domain
    # most of the time only P4 is with the domain
    df = df[(df.lon>-130) & (df.lon<-122) & (df.lat>42) & (df.lat<52)]

    # This dataset doesn't have unique numbers for each cast, if same stations
    # force lat and lon to be consistent throughout the given year
    for name in df.name.unique():
        df.loc[df.name==name,'lon'] = df[df.name==name].lon.values[0]
        df.loc[df.name==name,'lat'] = df[df.name==name].lat.values[0]

    # Each cast is associated with a different time (hh:mm), now assign arbitrary cid based on this
    unique = df.time.unique()
    ind = {time: cid for time, cid in zip(unique, range(len(unique)))}
    df['cid'] = df['time'].map(ind)

    # Next make derived quantities and do unit conversions
    # (1) Create CT, SA, and z
    # - pull out variables
    SP = df.SP.to_numpy()
    IT = df.IT.to_numpy()
    z = df['z'].to_numpy()
    lon = df.lon.to_numpy()
    lat = df.lat.to_numpy()
    # - do the conversions
    p = gsw.p_from_z(-z, lat)
    SA = gsw.SA_from_SP(SP, p, lon, lat)
    CT = gsw.CT_from_t(SA, IT, p)
    # - add the results to the DataFrame
    df['SA'] = SA
    df['CT'] = CT
    df['z'] = z
    rho = gsw.rho(SA,CT,p)

    # (2) units
    for vn in ['DO','NO3', 'PO4', 'SIO4','TA','DIC']:
        if (vn+' (umol/kg)') in df.columns:
            df[vn+' (uM)'] = (rho/1000) * df[vn+' (umol/kg)']

    # (3) retain only selected variables
    cols = ['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'z',
            'CT', 'SA', 'DO (uM)',
            'NO3 (uM)', 'PO4 (uM)', 'SiO4 (uM)',
            'TA (uM)', 'DIC (uM)']
    this_cols = [item for item in cols if item in df.columns]
    df = df[this_cols]

    print(' - processed %d casts' % ( len(df.cid.unique()) ))

    # Renumber cid to be increasing from zero in steps of one.
    df = obs_functions.renumber_cid(df)

    if len(df) > 0:
        # Save the data
        df.to_pickle(out_fn)
        info_df = obs_functions.make_info_df(df)
        info_df.to_pickle(info_out_fn)
