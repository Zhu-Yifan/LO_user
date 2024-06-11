"""
Code to process the WCOA 2021 bottle data into nceiCoastal database.
This dataset comes from a different source https://www.ncei.noaa.gov/access/ocean-carbon-acidification-data-system/oceans/Coastal/WCOA.html
"""
import pandas as pd
import numpy as np
import gsw

from lo_tools import Lfun, obs_functions

Ldir = Lfun.Lstart()

v_dict = {
    'time': ' time',
    'EXPOCODE': '',
    'Cruise_ID': 'cruise',
    'Section_ID': 'name',
    'Station_ID': 'cid',
    'Cast_number': '',
    'Rosette_Position': '',
    'Niskin_ID': '',
    'Niskin_flag': '',
    'Sample_ID': '',
    'Line_ID': '',
    'Date_UTC': '',
    'Year_UTC': '',
    'Month_UTC': '',
    'Day_UTC': '',
    'Time_UTC': '',
    'Yearday_UTC': '',
    'Latitude': 'lat',
    'Longitude': 'lon',
    'Depth_bottom': '',
    'Max_sample_depth': '',
    'CTDPRES': 'P (dbar)',
    'Depth': '',
    'CTDTEMP_ITS90': 'IT',
    'CTDSAL_PSS78': 'SP',
    'CTDSAL_flag': '',
    'Salinity_PSS78': '',
    'Salinity_flag': '',
    'CTDOXY': '',
    'CTDOXY_flag': 'DO (umol/kg)',
    'Oxygen_djg': '',
    'Oxygen': '',
    'Oxygen_flag': '',
    'DIC': 'DIC (umol/kg)',
    'DIC_flag': '',
    'TA': 'TA (umol/kg)',
    'TA_flag': '',
    'pH_T_measured': '',
    'TEMP_pH': '',
    'pH_flag': '',
    'Carbonate_measured': '',
    'TEMP_Carbonate': '',
    'Carbonate_flag': '',
    'Silicate': 'SiO4 (umol/kg)',
    'Silicate_flag': '',
    'Phosphate': 'PO4 (umol/kg)',
    'Phosphate_flag': '',
    'Nitrate': 'NO3 (umol/kg)',
    'Nitrate_flag': '',
    'Nitrite': 'NO2 (umol/kg)',
    'Nitrite_flag': '',
    'Ammonium': 'NH4 (umol/kg)',
    'Ammonium_flag': '',
    'Chl_a': '',
    'Chl_a_flag': '',
    'Methane_CH4': '',
    'Methane_CH4_flag': '',
    'SYNECHOCOCCUS': '',
    'SYNECHOCOCCUS_FLAG': '',
    'EUK_PHYTOPLANKTON': '',
    'EUK_PHYTOPLANKTON_FLAG': '',
    'LARGE_DIATOM': '',
    'LARGE_DIATOM_FLAG': '',
    'CRYPTOPHYTE': '',
    'CRYPTOPHYTE_FLAG': '',
    'BACTERIA': '',
    'BACTERIA_FLAG': '',
    'BACTERIA_HNA': '',
    'BACTERIA_HNA_FLAG': '',
    'BACTERIA_LNA': '',
    'BACTERIA_LNA_FLAG': '',
}

testing = True

if testing:
    year_list = [2021]
else:
    year_list = [2021]

# BOTTLE
source = 'WCOA2021'
otype = 'bottle'
in_dir0 = Ldir['data'] / 'obs' / source

# output location
out_dir = Ldir['LOo'] / 'obs' / 'nceiCoastal' / otype

load_data = True
for year in year_list:
    ys = str(year)
    print('\n' + ys)

    # name output files
    out_fn = out_dir / (ys + '.p')
    info_out_fn = out_dir / ('info_' + ys + '.p')

    if year in year_list:
        in_fn = in_dir0 / 'WCOA2021_Data_forSDIS_2022_09-28.csv'
        df0 = pd.read_csv(in_fn, low_memory=False, skiprows=[1],
                          parse_dates={'time': ['Year_UTC', 'Month_UTC', 'Day_UTC', 'Time_UTC']})
        """
        for some reason it raised error reading two extra empty rows, drop these 
        """
        df0 = df0.drop([2408, 2409])
        df0 = df0.reset_index(drop=True)
        df0['time'] = pd.to_datetime(df0['time'], format='ISO8601')
        load_data = False  # only load the first time
        # select one year
    t = pd.DatetimeIndex(df0.time)
    df1 = df0.loc[t.year == year, :].copy()

    # select and rename variables
    df = pd.DataFrame()
    for v in df1.columns:
        if v in v_dict.keys():
            if len(v_dict[v]) > 0:
                df[v_dict[v]] = df1[v]

    # missing data is -999
    df[df == -999] = np.nan

    # a little more cleaning up
    df = df.dropna(axis=0, how='all')  # drop rows with no good data
    df = df[df.time.notna()]  # drop rows with bad time
    df = df.reset_index(drop=True)

    #  now limit the geographical region to the model domain

    df = df[(df.lon > -130) & (df.lon < -122) & (df.lat > 42) & (df.lat < 52)]

    # This dataset doesn't have unique numbers for each cast, if same stations, force lat and lon to be consistent
    # throughout the given year
    for name in df.name.unique():
        df.loc[df.name == name, 'lon'] = df[df.name == name].lon.values[0]
        df.loc[df.name == name, 'lat'] = df[df.name == name].lat.values[0]

    # Next make derived quantities and do unit conversions
    # (1) Create CT, SA, and z
    # - pull out variables
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
    rho = gsw.rho(SA, CT, p)

    # (2) units
    for vn in ['DO', 'NO3', 'NO2', 'NH4', 'PO4', 'SIO4', 'TA', 'DIC']:
        if (vn + ' (umol/kg)') in df.columns:
            df[vn + ' (uM)'] = (rho / 1000) * df[vn + ' (umol/kg)']

    # (3) retain only selected variables
    cols = ['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'z',
            'CT', 'SA', 'DO (uM)',
            'NO3 (uM)', 'NO2 (uM)', 'NH4 (uM)', 'PO4 (uM)', 'SiO4 (uM)',
            'TA (uM)', 'DIC (uM)']
    this_cols = [item for item in cols if item in df.columns]
    df = df[this_cols]

    print(' - processed %d casts' % (len(df.cid.unique())))

    # Renumber cid to be increasing from zero in steps of one.
    df = obs_functions.renumber_cid(df)

    if len(df) > 0:
        # Save the data
        df.to_pickle(out_fn)
        info_df = obs_functions.make_info_df(df)
        info_df.to_pickle(info_out_fn)
