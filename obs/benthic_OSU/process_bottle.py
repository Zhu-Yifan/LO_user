
"""
Code to process the bottle data collected bottom boundary layer samples collected aboard the R/V Oceanus during ten cruises from 2017-2019 from the Oregon shelf and slope.

"""

import pandas as pd
import numpy as np
import gsw
from time import time as Time
from pathlib import Path
import PyCO2SYS as pyco2
from lo_tools import Lfun, obs_functions
Ldir = Lfun.Lstart()

v_dict = {

    'Cruise_Name':'cruise',
    'Event':'',
    'Latitude':'lat',
    'Longitude':'lon',
    'Niskin_bottle':'',
    'ISO_DateTime_UTC':'time',
    'DateTime_PST':'',
    'Depth':'z',
    'Altitude':'',
    'CTD_Temp':'IT',
    'CTD_Salinity':'SP',
    'CTD_Cond':'',
    'CTD_Density':'',
    'CTD_DO':'',
    'CTD_DO_2':'',
    'Oxygen':'',
    'O2_Conc_Winkler':'',
    'O2_Conc_Winkler_2':'DO (uM)',
    'TCO2':'DIC (umol/kg)',
    'pco2_in_situ': 'pCO2',
    'Volume_filtered':'',
    'TSS':'',
    'TN':'',
    'OC':'',
    'PO4':'PO4 (uM)',
    'Nitrate_Nitrite': 'N+N (uM)',
    'Silicate': 'SiO4 (uM)',
    'NO2': 'NO2 (uM)',
    'NH4': 'NH4 (uM)',

    }

# BOTTLE
source = 'benthic_OSU'
otype = 'bottle'
in_dir0 = Ldir['data'] / 'obs' / source

testing = False
if testing:
    year_list = [2017]
else:
    
    year_list = range(2017,2020)

# output location
out_dir = Ldir['LOo'] / 'obs' / source / otype 

Lfun.make_dir(out_dir)

tt0 = Time()
in_fn = in_dir0 / 'ctd_data.csv'
df0 = pd.read_csv(
    in_fn,
    low_memory=False,
    parse_dates=['ISO_DateTime_UTC'],
    na_values=['nd']
)

df0['ISO_DateTime_UTC'] = df0['ISO_DateTime_UTC'].dt.tz_localize(None)
df0['O2_Conc_Winkler_2'] = df0['O2_Conc_Winkler_2'].fillna(df0['CTD_DO_2'])

for year in year_list:
    ys = str(year)
    print('\n'+ys)
    # name output files
    out_fn = out_dir / (ys + '.p')
    info_out_fn = out_dir / ('info_' + ys + '.p')
    df00 = pd.DataFrame()
    # for each year
    df1 = df0.loc[df0['ISO_DateTime_UTC'].dt.year==year,:].copy()
    if df1.empty:
        continue
    # select and rename variables
    df = pd.DataFrame()
    for v in df1.columns:
        if v in v_dict.keys():
            if len(v_dict[v]) > 0:
                df[v_dict[v]] = df1[v]
    num_cols = [
        'SP', 'IT', 'NO2 (uM)', 'N+N (uM)', 'PO4 (uM)', 'z',
        'SiO4 (uM)', 'DO (uM)', 'NH4 (uM)', 'DIC (umol/kg)', 'pCO2'
    ]

    for col in num_cols:
        if col in df.columns:
            df[df[col]< 0] = np.nan
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(axis=0, how='all')
    df = df[df.time.notna()]
    df = df.reset_index(drop=True)

    df['lon'] = df['lon'].round(3)
    df['lat'] = df['lat'].round(3)
    df['cid'] = df.groupby(['lat', 'lon', 'time']).ngroup() + 1

    df['NO3 (uM)'] = df['N+N (uM)'] - df['NO2 (uM)']

    SP = df.SP.to_numpy()
    IT = df.IT.to_numpy()
    z = -1 * df['z'].to_numpy()

    lon = df.lon.to_numpy()
    lat = df.lat.to_numpy()

    p = gsw.p_from_z(z, lat)
    # - do the conversions
    SA = gsw.SA_from_SP(SP, p, lon, lat)
    CT = gsw.CT_from_t(SA, IT, p)
    rho = gsw.rho(SA,CT,p)

    # (2) units
    for vn in ['NH4', 'PO4', 'SiO4']:
        if (vn+' (uM)') in df.columns:
            df[vn+' (umol/kg)'] = df[vn+' (uM)'] * 1000/rho

    SiO4 = df['SiO4 (umol/kg)'].to_numpy()
    PO4 = df['PO4 (umol/kg)'].to_numpy()
    NH4 = df['NH4 (umol/kg)'].to_numpy()

    TIC = df['DIC (umol/kg)'].to_numpy()
    pCO2 = df['pCO2'].to_numpy()

    # - add the results to the DataFrame
    df['SA'] = SA
    df['CT'] = CT
    df['z'] = z

    # derive TA (umol/lg)
    kwargs = dict(
    par1 = TIC,  # Value of the first parameter, unit: umol/kg
    par2 = pCO2,  # unit: μatm
    par1_type = 2 ,  # The first parameter supplied is of type "2", which is "DIC"
    par2_type = 4,  # The second parameter supplied is of type "4", which is "pCO2"
    salinity = SP,  # Salinity of the sample
    temperature = IT,  # Temperature at input conditions; in situ temperature
    pressure = p,        # # lab pressure (input conditions) in dbar, ignoring the atmosphere
    total_silicate = SiO4,  # Concentration of silicate in the sample (in umol/kg)
    total_phosphate = PO4,  # Concentration of phosphate in the sample (in umol/kg)
    total_ammonia = NH4,  # total ammonia in μmol/kg-sw
    total_sulfide = 0.0,  # total sulfide in μmol/kg-sw
    opt_pH_scale = 1,     # tell PyCO2SYS: "the pH input is on the Total scale"
    opt_k_carbonic = 7,  # Choice of H2CO3 and HCO3- dissociation constants K1 and K2 ("7" means the carbonic acid dissociation constants of Mehrbach et al.1973; without certain species aka "Peng" (2 < T < 35 °C, 19 < S < 43, NBS scale, real seawater)
    opt_k_bisulfate = 1,  # Choice of HSO4- dissociation constants KSO4 ("1" means "Dickson 1990), it is consistent with LO_parameterization
    opt_total_borate = 1,  # tell PyCO2SYS: "use borate:salinity of U74". It is consistent with LO_parameterization
    opt_k_fluoride = 1, # Choice of HF dissociation constants: ("1" means "Dickson and Riley 1979). it is consistent with LO_parameterization
    )
    print("Input conditions have been set!")

    # Run CO2SYS
    CO2dict = pyco2.sys(**kwargs)
    print('PyCO2SYS ran successfully!')

    # Extract the calculated variables
    # varARAG = CO2dict['saturation_aragonite']
    varAlk = CO2dict['alkalinity']

    df['TA (umol/kg)'] = varAlk

    for vn in ['TA','DIC']:
        if (vn+' (umol/kg)') in df.columns:
            df[vn+' (uM)'] = (rho/1000) * df[vn+' (umol/kg)']

    # add cid
    unique = df.time.unique()
    ind = {time: cid for time, cid in zip(unique, range(len(unique)))}

    df['cid'] = df['time'].map(ind)
    # add name (string version)
    name_map = {time: f'St{cid}' for time, cid in ind.items()}
    df['name'] = df['time'].map(name_map)

    #  retain only selected variables
    cols = ['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'z',
            'CT', 'SA', 'DO (uM)',
            'NO3 (uM)', 'NO2 (uM)', 'NH4 (uM)', 'PO4 (uM)', 'SiO4 (uM)',
            'TA (uM)', 'DIC (uM)']

    this_cols = [item for item in cols if item in df.columns]
    df = df[this_cols]

    # append to df00
    if df.shape[0] > 1:
        df00 = pd.concat([df00, df], ignore_index=True)

    #  Save the data
    if len(df00) > 0:
        df00.to_pickle(out_fn)
        info_df = obs_functions.make_info_df(df00)
        info_df.to_pickle(info_out_fn)

    print(f'processed {np.max(df00.cid)} stations in year {year}')

print('Total time = %d sec' % (int(Time()-tt0)))


