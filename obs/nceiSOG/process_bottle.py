"""
Code to process the bottle profile carbon data collected in the Strait of Georgia, ~ 300 casts

NOTE: There are multiple files for a given year, or multiple datasets for different year.
we want to combine those files to yearly for an easier process
"""

import pandas as pd
import numpy as np
import gsw
import glob
import os
import re
from lo_tools import Lfun, obs_functions
Ldir = Lfun.Lstart()

# BOTTLE
source = 'nceiSOG'
otype = 'bottle'
in_dir0 = Ldir['data'] / 'obs' / source

# output location
out_dir = Ldir['LOo'] / 'obs' / source / otype
Lfun.make_dir(out_dir)

testing = False
if testing:
    year_list = [2003]
    ncei_list = {
        # '0173514': '',
        # '0225526': '',
        # '0225534': '',
        '0232540': '',
        # '0297364':  'Qu39',
        # '0169412':  'wcoa2016',
    }
else:
    # no year 2013
    # year_list = [2014]
    year_list = [2003] + list(range(2010, 2012+1)) + list(range(2014, 2023+1))
    ncei_list = {
        '0173514': '',
        '0225526': '',
        '0225534': '',
        '0232540': '',
        '0297364':  'Qu39', # this dataset doesn't have nutrient
        '0169412':  'wcoa2016',
    }

# get the folder structure
def get_folder_info(directory, name):
    for root, dirs, files in os.walk(directory):
        for folder in dirs:
            match = re.search(r"\d+\.\d+$", folder)
            ver = match.group(0) if match else None
            if name in folder:
                return os.path.join(root, folder), ver

# combine all six datasets together then split into yearly
# six different datasets, handle each differently
for ncei in ncei_list.keys():
    print(ncei)
    if ncei == '0173514':
        v_dict = {
            'EXPOCODE':'',
            'cruise':'cruise',
            'Datetime': 'time',
            'STNNBR':'name',
            'CASTNO':'cid',
            'BTLNBR':'',
            'YEAR':'',
            'MONTH':'',
            'DAY':'',
            'LONGITUDE':'lon',
            'LATITUDE':'lat',
            'CTDPRS':'P (dbar)',
            'CTDTMP':'IT',
            'CTDSAL':'SP',
            'CTDSAL_FLAG_W':'',
            'OXYGEN':'DO (umol/kg)',
            'OXYGEN_FLAG_W':'',
            'TCARBN':'DIC (umol/kg)',
            'TCARBN_FLAG_W':'',
            'ALKALI':'TA (umol/kg)',
            'ALKALI_FLAG_W':'',
            'NITRAT':'NO3 (umol/kg)',
            'NITRAT_FLAG_W':'',
            'SILCAT':'SiO4 (umol/kg)',
            'SILCAT_FLAG_W':'',
            'PHSPHT':'PO4 (umol/kg)',
            'PHSPHT_FLAG_W':'',
        }
        info = get_folder_info(in_dir0,ncei)
        in_dir = info[0] + '/' + ncei + '/' + info[1] + '/' + 'data' + '/' + '0-data'
        in_files = glob.glob(os.path.join(in_dir, '*.csv'))
        # Load each CSV file and concatenate them into a single DataFrame
        data_list = [pd.read_csv(file, header=23, skiprows=[24]) for file in in_files]
        df = pd.concat(data_list, ignore_index=True)
        df['cruise'] = 'CCGS time series'
        df['date'] = pd.to_datetime(df[['YEAR', 'MONTH', 'DAY']])
        # dataset lacks hour, now force it to be noon
        df['Datetime'] = df['date'] + pd.Timedelta(hours=12)
        # select and rename variables
        df1 = pd.DataFrame()
        for v in df.columns:
            if v in v_dict.keys():
                if len(v_dict[v]) > 0:
                    df1[v_dict[v]] = df[v]
        df1 = df1[df1['IT'].notna()]
        df1 = df1[df1['SP'].notna()]
        df1 = df1[df1['DIC (umol/kg)'].notna()]
        # the cid
        df1['cid'] = pd.factorize(df1[['time', 'lat', 'lon']].apply(tuple, axis=1))[0]
        # (3) retain only selected variables
        cols = ['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'P (dbar)',
                'IT', 'SP', 'DO (umol/kg)',
                'NO3 (umol/kg)', 'NH4 (umol/kg)', 'PO4 (umol/kg)', 'SiO4 (umol/kg)',
                'TA (umol/kg)', 'DIC (umol/kg)']
        this_cols = [item for item in cols if item in df1.columns]
        df1 = df1[this_cols]

    elif ncei == '0297364':
        v_dict = {
            'EXPOCODE':'',
            'Cast_number':'cid',
            'Cruise ID':'cruise',
            'Station': 'name',
            'Year_UTC':'',
            'Month_UTC':'',
            'Day_UTC':'',
            'Hour_UTC':'',
            'Date_time (yyyy-mm-dd hh:mm:ss)':'time',
            'DOY_UTC':'',
            'Latitude':'lat',
            'Longitude':'lon',
            'CO2 data QC flag':'',
            'CTD Pres (bdar)':'P (dbar)',
            'CTD T (deg C)':'IT',
            'CTD S (PSS-78)':'SP',
            'CTD O2 (umol/kg)':'DO (umol/kg)',
            'TCO2 (umol/kg)':'DIC (umol/kg)',
            'Analysis T (deg C)':'',
            'pCO2@analysisT (uatm)':'',
            'headspace cor TCO2 (umol/kg)':'',
            'Alkalinity (umol/kg)':'TA (umol/kg)',
            'pCO2@insituT&P (uatm)':'pCO2 (uatm)',
            'pH@insituT&P': 'pH',
            'Omega_calcite': '',
            'Omega_aragonite': '',
            'Revelle factor': '',
            'composite mean T (deg C)':'',
            'composite mean S (PSS-78)':'',
            'composite mean O2 (umol/kg)':'',
            'composite mean TCO2 (umol/kg)':'',
            'composite mean alkalinity (umol/kg)':'',
            'composite mean pCO2@instuT&P (uatm)':'',
            'composite mean pH@instuT&P':'',
            'composite mean omega_calcite':'',
            'composite mean omega_aragonite':'',
            'composite mean Revelle factor':'',

        }
        info = get_folder_info(in_dir0,ncei)
        in_dir = info[0] + '/' + ncei + '/' + info[1] + '/' + 'data' + '/' + '0-data'
        print(in_dir)
        in_file = in_dir + '/' + 'QU39_inorganic_carbon_data_2016_2023.xls'
        df = pd.read_excel(in_file, header=4, parse_dates=['Date_time (yyyy-mm-dd hh:mm:ss)'])
        df['Station'] = 'QU39'
        # select and rename variables
        df2 = pd.DataFrame()
        for v in df.columns:
            if v in v_dict.keys():
                if len(v_dict[v]) > 0:
                    df2[v_dict[v]] = df[v]
        df2 = df2[df2['IT'].notna()]
        df2 = df2[df2['SP'].notna()]
        df2 = df2[df2['DIC (umol/kg)'].notna()]
        df2['cid'] = pd.factorize(df2['time'])[0]
        # (3) retain only selected variables
        cols = ['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'P (dbar)',
                'IT', 'SP', 'DO (umol/kg)',
                'NO3 (umol/kg)', 'NH4 (umol/kg)', 'PO4 (umol/kg)', 'SiO4 (umol/kg)',
                'TA (umol/kg)', 'DIC (umol/kg)']
        this_cols = [item for item in cols if item in df2.columns]
        df2 = df2[this_cols]

    elif ncei == '0169412':
        v_dict = {
            'EXPOCODE':'',
            'CRUISE_ID':'cruise',
            'STATION_ID':'name',
            'CAST_NO':'cid',
            'NISKIN_ID':'',
            'NISKIN_FLAG':'',
            'SAMPLE_ID':'',
            'LINE':'',
            'YEAR_UTC':'',
            'MONTH_UTC':'',
            'DAY_UTC':'',
            'TIME_UTC':'',
            'Datetime':'time',
            'LATITUDE_DECIMAL':'lat',
            'LONGITUDE_DECIMAL':'lon',
            'DEPTH_BOTTOM_METER':'',
            'CTDPRESSURE_DBAR':'P (dbar)',
            'CTDTMP_ITS90_DEG_C':'IT',
            'CTDSAL_PSS78':'SP',
            'SALINITY_PSS78':'',
            'SALINTY_FLAG':'',
            'CTDOXYGEN_UMOL_KG':'DO (umol/kg)',
            'OXYGEN_FLAG':'',
            'DIC_UMOL_KG':'DIC (umol/kg)',
            'DIC_FLAG':'',
            'TA_UMOL_KG':'TA (umol/kg)',
            'TA_FLAG':'',
            'PH_TOT_MEA':'',
            'TMP_PH_DEG_C':'',
            'PH_FLAG':'',
            'CARBONATE_UMOL_KG':'',
            'TMP_CARBONATE_DEG_C':'',
            'CARBONATE_FLAG':'',
            'SILICATE_UMOL_KG':'SiO4 (umol/kg)',
            'NITRATE_UMOL_KG':'NO3 (umol/kg)',
            'NITRITE_UMOL_KG':'NO2 (umol/kg)',
            'PHOSPHATE_UMOL_KG':'PO4 (umol/kg)',
            'AMMONIUM_UMOL_KG':'NH4 (umol/kg)',
            'NUTRIENTS_FLAG':'',
            'CHL_A_UG_L_PC':'',
            'CHL_A_UG_L_GFF':'',
            'Chl_a_flag':'',
            'ACCESSION':'',
        }

        info = get_folder_info(in_dir0,ncei)
        in_dir = info[0] + '/' + ncei + '/' + info[1] + '/' + 'data' + '/' + '0-data'
        print(in_dir)
        in_file = in_dir + '/' + 'W05_WCOA2016R_djg_v2.xlsx'
        df = pd.read_excel(in_file)
        df['date'] = pd.to_datetime(df[['YEAR_UTC', 'MONTH_UTC', 'DAY_UTC']].astype(str).agg('-'.join, axis=1))
        df['TIME_UTC'] = pd.to_timedelta(df['TIME_UTC'].astype(str))
        df['Datetime'] = df['date'] + df['TIME_UTC']
        # missing data is -999
        df[df==-999] = np.nan
        # select and rename variables
        df3 = pd.DataFrame()
        for v in df.columns:
            if v in v_dict.keys():
                if len(v_dict[v]) > 0:
                    df3[v_dict[v]] = df[v]
        df3 = df3[df3['IT'].notna()]
        df3 = df3[df3['SP'].notna()]
        df3 = df3[df3['DIC (umol/kg)'].notna()]
        #This dataset doesn't have unique numbers for each cast,
        # if same stations, force lat and lon to be consistent throughout the given year
        for name in df3.name.unique():
            df3.loc[df3.name==name,'time'] = df3[df3.name==name].time.values[0]

        df3['cid'] = pd.factorize(df3[['time', 'lat', 'lon','name']].apply(tuple, axis=1))[0]
        # (3) retain only selected variables
        cols = ['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'P (dbar)',
                'IT', 'SP', 'DO (umol/kg)',
                'NO3 (umol/kg)', 'NH4 (umol/kg)', 'PO4 (umol/kg)', 'SiO4 (umol/kg)',
                'TA (umol/kg)', 'DIC (umol/kg)']
        this_cols = [item for item in cols if item in df3.columns]
        df3 = df3[this_cols]
        # only keep the Salish Sea region, this will only keep 2 stations in the SOG from WCOA2016 cruise
        df3 = df3[(df3.lon>-124.98) & (df3.lon<-122.95) & (df3.lat>48.22) & (df3.lat<51.5)]


    elif ncei == '0225526':
        v_dict = {
            'EXPOCODE':'',
            'CRUISE_ID':'',
            'PLATFORM':'cruise',
            'SAMPLE_NUMBER':'',
            'LINE_NUMBER':'',
            'STATION_ID':'name',
            'YEAR':'',
            'MONTH':'',
            'DAY':'',
            'Datetime': 'time',
            'LATITUDE_DEC':'lat',
            'LONGITUDE_DEC':'lon',
            'DEPTH_BOTTOM_METER':'',
            'CTDPRS_DBAR':'P (dbar)',
            'CTDPRS_FLAG_W':'',
            'CTDTMP_ITS90_DEG_C':'IT',
            'DRAWTMP_DEG_C':'',
            'CTDSAL_PSS78':'SP',
            'CTDSAL_FLAG':'',
            'SALINITY_PSS78':'',
            'SALINITY_FLAG':'',
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
        }
        info = get_folder_info(in_dir0,ncei)
        in_dir = info[0] + '/' + ncei + '/' + info[1] + '/' + 'data' + '/' + '0-data'
        print(in_dir)
        in_file = in_dir + '/' + '2014-50_Datafile.csv'
        df = pd.read_csv(in_file)
        df['date'] = pd.to_datetime(df[['YEAR', 'MONTH', 'DAY']])
        # dataset lacks hour, now force it to be noon
        df['Datetime'] = df['date'] + pd.Timedelta(hours=12)
        # select and rename variables
        df4 = pd.DataFrame()
        for v in df.columns:
            if v in v_dict.keys():
                if len(v_dict[v]) > 0:
                    df4[v_dict[v]] = df[v]
        df4 = df4[df4['IT'].notna()]
        df4 = df4[df4['SP'].notna()]
        df4 = df4[df4['DIC (umol/kg)'].notna()]
        df4['cid'] = pd.factorize(df4[['time', 'lat', 'lon','name']].apply(tuple, axis=1))[0]
        # (3) retain only selected variables
        cols = ['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'P (dbar)',
                'IT', 'SP', 'DO (umol/kg)',
                'NO3 (umol/kg)', 'NH4 (umol/kg)', 'PO4 (umol/kg)', 'SiO4 (umol/kg)',
                'TA (umol/kg)', 'DIC (umol/kg)']
        this_cols = [item for item in cols if item in df4.columns]
        df4 = df4[this_cols]

    elif ncei == '0225534':
        v_dict = {
            'EXPOCODE':'',
            'CRUISE_ID':'',
            'PLATFORM':'cruise',
            'SAMPLE_NUMBER':'',
            'LINE_NUMBER':'',
            'STATION_ID':'name',
            'YEAR':'',
            'MONTH':'',
            'DAY':'',
            'Datetime':'time',
            'LATITUDE_DEC':'lat',
            'LONGITUDE_DEC':'lon',
            'DEPTH_BOTTOM_METER':'',
            'CTDPRS_DBAR':'P (dbar)',
            'CTDPRS_FLAG_W':'',
            'CTDTMP_ITS90_DEG_C':'IT',
            'DRAWTMP_DEG_C':'',
            'CTDSAL_PSS78':'SP',
            'CTDSAL_FLAG':'',
            'SALINITY_PSS78':'',
            'SALINITY_FLAG':'',
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

        }
        info = get_folder_info(in_dir0,ncei)
        in_dir = info[0] + '/' + ncei + '/' + info[1] + '/' + 'data' + '/' + '0-data'
        print(in_dir)
        in_file = in_dir + '/' + '2015-17_Datafile.csv'
        df = pd.read_csv(in_file)
        df['date'] = pd.to_datetime(df[['YEAR', 'MONTH', 'DAY']])
        # dataset lacks hour, now force it to be noon
        df['Datetime'] = df['date'] + pd.Timedelta(hours=12)
        # select and rename variables
        df5 = pd.DataFrame()
        for v in df.columns:
            if v in v_dict.keys():
                if len(v_dict[v]) > 0:
                    df5[v_dict[v]] = df[v]
        df5 = df5[df5['IT'].notna()]
        df5 = df5[df5['SP'].notna()]
        df5 = df5[df5['DIC (umol/kg)'].notna()]
        df5['cid'] = pd.factorize(df5[['time', 'lat', 'lon','name']].apply(tuple, axis=1))[0]
        # (3) retain only selected variables
        cols = ['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'P (dbar)',
                'IT', 'SP', 'DO (umol/kg)',
                'NO3 (umol/kg)', 'NH4 (umol/kg)', 'PO4 (umol/kg)', 'SiO4 (umol/kg)',
                'TA (umol/kg)', 'DIC (umol/kg)']
        this_cols = [item for item in cols if item in df5.columns]
        df5 = df5[this_cols]

    elif ncei == '0232540':
        v_dict = {
            'EXPOCODE':'',
            'CRUISE_ID':'',
            'PLATFORM':'cruise',
            'SAMPLE_NUMBER':'',
            'STATION_ID':'name',
            'YEAR_UTC':'',
            'MONTH_UTC':'',
            'DAY_UTC':'',
            'Datetime':'time',
            'LATITUDE_DEC':'lat',
            'LONGITUDE_DEC':'lon',
            'CTDPRS_DBAR':'P (dbar)',
            'CTDPRS_FLAG_W':'',
            'CTDTMP_ITS90_DEG_C':'IT',
            'CTDTMP_FLAG_W':'',
            'CTDSAL_PSS78':'SP',
            'CTDSAL_FLAG_W':'',
            'SALNTY_PSS78':'',
            'SALNTY_FLAG':'',
            'OXYGEN_UMOL_KG':'DO (umol/kg)',
            'OXYGEN_FLAG_W':'',
            'DIC_UMOL_KG':'DIC (umol/kg)',
            'DIC_FLAG_W':'',
            'TA_UMOL_KG':'TA (umol/kg)',
            'TA_FLAG_W':'',
            'NITRATE_UMOL_KG':'NO3 (umol/kg)',
            'NITRATE_NITRITE_FLAG_W':'',
            'SILICATE_UMOL_KG':'SiO4 (umol/kg)',
            'SILICATE_FLAG_W':'',
            'PHOSPHATE_UMOL_KG':'PO4 (umol/kg)',
            'PHOSPHATE_FLAG_W':'',

        }

        info = get_folder_info(in_dir0,ncei)
        in_dir = info[0] + '/' + ncei + '/' + info[1] + '/' + 'data' + '/' + '0-data'
        print(in_dir)
        in_file = in_dir + '/' + 'John_Strickland_2015-2017_Datafile.csv'
        df = pd.read_csv(in_file)
        df['date'] = pd.to_datetime(df[['YEAR_UTC', 'MONTH_UTC', 'DAY_UTC']].astype(str).agg('-'.join, axis=1))
        df['Datetime'] = df['date'] + pd.Timedelta(hours=12)
        # select and rename variables
        df6 = pd.DataFrame()
        for v in df.columns:
            if v in v_dict.keys():
                if len(v_dict[v]) > 0:
                    df6[v_dict[v]] = df[v]
        df6 = df6[df6['IT'].notna()]
        df6 = df6[df6['SP'].notna()]
        df6 = df6[df6['DIC (umol/kg)'].notna()]
        df6['cid'] = pd.factorize(df6[['time', 'lat', 'lon']].apply(tuple, axis=1))[0]

        # (3) retain only selected variables
        cols = ['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'P (dbar)',
                'IT', 'SP', 'DO (umol/kg)',
                'NO3 (umol/kg)', 'NH4 (umol/kg)', 'PO4 (umol/kg)', 'SiO4 (umol/kg)',
                'TA (umol/kg)', 'DIC (umol/kg)']
        this_cols = [item for item in cols if item in df6.columns]
        df6 = df6[this_cols]

# List of DataFrames to concatenate
dfs = [df1, df2, df3, df4, df5, df6]
# Concatenate all DataFrames, including all columns
df = pd.concat(dfs, join='outer', axis=0, ignore_index=True)
# missing data is -999
df[df==-999] = np.nan
df = df.dropna(axis=0, how='all') # drop rows with no good data
df = df[df.time.notna()] # drop rows with bad time
df = df.reset_index(drop=True)

#Next make derived quantities and do unit conversions
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
rho = gsw.rho(SA,CT,p)

# (2) units
for vn in ['DO','NO3', 'NH4', 'PO4', 'SIO4','TA','DIC']:
    if (vn+' (umol/kg)') in df.columns:
        df[(vn+' (umol/kg)')] = pd.to_numeric(df[(vn+' (umol/kg)')], errors='coerce')
        df[vn+' (uM)'] = (rho/1000) * df[vn+' (umol/kg)']

# (3) retain only selected variables
cols = ['cid', 'cruise', 'time', 'lat', 'lon', 'name', 'z',
        'CT', 'SA', 'DO (uM)',
        'NO3 (uM)', 'NH4 (uM)', 'PO4 (uM)', 'SiO4 (uM)',
        'TA (uM)', 'DIC (uM)']
this_cols = [item for item in cols if item in df.columns]
df = df[this_cols]

# keep data when DIC is not NaN
df = df[df['DIC (uM)'].notna()]
# force the time to datetime format
df['time'] = pd.to_datetime(df['time'], errors='coerce')

# You can now work with df0 for each specific year
cast = 0
for year in year_list:
    ys = str(year)
    print('\n'+ys)
    # name output files
    out_fn = out_dir / (ys + '.p')
    info_out_fn = out_dir / ('info_' + ys + '.p')
    df0 = df[df['time'].dt.year == year]
    # # Renumber cid to be increasing from zero in steps of one.
    df0 = obs_functions.renumber_cid(df0)
    if len(df0) > 0:
        # Save the data
        df0.to_pickle(out_fn)
        info_df = obs_functions.make_info_df(df0)
        info_df.to_pickle(info_out_fn)

    print('  - processed %d casts' % (len(df0.cid.unique())))
    cast += len(df0.cid.unique())

print('\n total processed %d casts' % cast)