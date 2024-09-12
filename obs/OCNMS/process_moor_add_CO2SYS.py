"""
code to process the matlab mooring dataset (2000-2023) compiled by Craig Risen at OSU
this script only extract bottom package: CTD+DO

and then use empirical relationship from Simone Alin to derive DIC and TA, pCO2, pH, OmA

"""

from scipy.io import loadmat
import pandas as pd
import xarray as xr
import numpy as np
import gsw
from datetime import datetime, timedelta
from time import time as Time

from lo_tools import Lfun
Ldir = Lfun.Lstart()

# input location
source = 'OCNMS'
otype = 'moor'
in_dir = Ldir['data'] / 'obs' / source / otype

# output location
out_dir = Ldir['LOo'] / 'obs' / source / otype

Lfun.make_dir(out_dir,clean = True)
# this is all the mooring sites maintained
sn_name_dict = {
    'CA015':'Cape Alava 15m',
    'CA042':'Cape Alava 42m',
    'CA065':'Cape Alava 65m',
    'CA100':'Cape Alava 100m',
    'CE015':'Cape Elizabeth 15m',
    'CE042':'Cape Elizabeth 42m',
    'CE065':'Cape Elizabeth 65m',
    'KL015':'Kalaloch 15m',
    'KL027':'Kalaloch 27m',
    'KL050':'Kalaloch 50m',
    'MB015':'Makah Bay 15m',
    'MB042':'Makah Bay 42m',
    'TH015':'Teahwhit Head 15m',
    'TH042':'Teahwhit Head 42m',
    'TH065':'Teahwhit Head 65m'

}

sn_loc_dict = {
    'CA015': [-124.7568, 48.1663],
    'CA042': [-124.8234, 48.1660],
    'CA065': [-124.8949, 48.1659],
    'CA100': [-124.9319, 48.1658],

    'CE015': [-124.3481, 47.3568],
    'CE042': [-124.4887, 47.3531],
    'CE065': [-124.5669, 47.3528],

    'KL015': [-124.4284, 47.6008],
    'KL027': [-124.4971, 47.5946],
    'KL050': [-124.6112, 47.5933],

    'MB015': [-124.6768, 48.3254],
    'MB042': [-124.7354, 48.3240],

    'TH015': [-124.6195, 47.8761],
    'TH042': [-124.7334, 47.8762],
    'TH065': [-124.7967, 47.8767]

}

v_dict = {

    'time':'matlab_time',
    'time_daily':'',
    'altitude':'',
    'depth':'depth',
    'temp':'IT',
    'temp_daily':'',
    'deploy_dates':'',
    'sal': 'SP',
    'sal_daily':'',
    'pres': 'P (dbar)',
    'pres_daily': '',
    'oxy':'oxy_mg',
    'oxy_daily': ''
}

in_fn = in_dir / 'OCNMSMooringDataBySite_2000_2023.mat'
moor_dict = loadmat(in_fn)
# print(moor_dict.keys())

# function to covert matlab datenum to datetime
def matlab_to_datetime(matlab_datenum):
    days = matlab_datenum - 366
    fractional_days = matlab_datenum % 1
    return datetime.fromordinal(int(days)) + timedelta(days=fractional_days)

tt0 = Time()
for sn in moor_dict.keys():
    if sn in sn_name_dict.keys():
        print(sn)
        out_fn = out_dir / (sn + '_2000_2023_hourly.nc')
        moor_data = moor_dict[sn][0]
        df0 = {}
        df = pd.DataFrame()
        # df1 = pd.DataFrame()
        field_list = moor_data.dtype.names
        for field in field_list:
            # print(field)
            # we only need bottom DO at present
            if field == 'CTPO':
                CTPO = moor_data[field][0]
                vn_list = CTPO.dtype.names
                # print(vn_list)

                for v in vn_list:
                    # print(v)
                    if v in v_dict.keys():
                        # print(v_dict[v])
                        if len(v_dict[v]) > 0:
                            # Use append() method to add elements to the list
                            if v_dict[v] not in df0:
                                df0[v_dict[v]] = []  # Initialize the list if it doesn't exist
                                df0[v_dict[v]].append(CTPO[v][0])
                            if v_dict[v] == 'matlab_time':
                                df[str(v_dict[v])] = df0[str(v_dict[v])][0][0][0,:]
                            elif v_dict[v] == 'depth':
                                df[str(v_dict[v])] =  np.repeat(df0[str(v_dict[v])][0][0], len(df['matlab_time']))
                            else:
                                df[str(v_dict[v])] = df0[str(v_dict[v])][0][0][:,0]

                df = df.dropna(axis=0, how='all')
                df = df.reset_index(drop=True)
                # (1) Create CT, SA, and z
                # - pull out variables
                SP = df.SP.to_numpy()
                IT = df.IT.to_numpy()
                p = df['P (dbar)'].to_numpy()
                # z = gsw.z_from_p(p, lat)
                z = df['depth'].to_numpy()
                lon = np.repeat(sn_loc_dict[sn][0], len(df['matlab_time']))
                lat = np.repeat(sn_loc_dict[sn][1], len(df['matlab_time']))
                SA = gsw.SA_from_SP(SP, p, lon, lat)
                CT = gsw.CT_from_t(SA, IT, p)
                PT = gsw.pt_from_t(SA, IT, p, 0)
                rho = gsw.rho(SA,CT,p)
                sigma_theta = gsw.sigma0(SA, CT)
                # - add the results to the DataFrame
                df['lat'] = lat
                df['lon'] = lon
                df['SA'] = SA
                df['CT'] = CT
                df['PT'] = PT
                z = z * -1
                df['z'] = z

                # - do the conversions
                df['DO (uM)'] = df['oxy_mg'] * 1000/32

                df['time'] = df['matlab_time'].apply(matlab_to_datetime)
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

                # calcite saturation state
                k0 = 0.457123751801731
                k1 = 0.00835889521467273
                k2 = -1.74785679635637
                k3 = 0.167778930558794
                k4 = -0.00464353794118862
                k5 = 0.163648318853162
                df['OmC'] = k0 + k1 * df['DO (umol/kg)'] + k2 * IT + k3 * IT**2 + k4 * IT**3 + k5 * SP

                k0 =  7.7087627350226
                k1 = 0.00229938216798432
                k2 = -0.262353368526682
                k3 = 0.0248535430695101
                k4 = -0.000732366152154055
                k5 = 0.0172593555271068
                df['pH'] = k0 + k1 * df['DO (umol/kg)'] + k2 * IT + k3 * IT**2 + k4 * IT**3 + k5 * SP

                # pCO2 (at in situ T, S, P)
                k0 =  1581.92373785639
                k1 = 0.0120707443361734
                k2 = -8.66508784885318
                k3 = 66.2027854732329
                k4 = -3.64420717525608
                df['pCO2'] = k0 + k1 * (df['DO (umol/kg)'])**2 + k2 * df['DO (umol/kg)'] + k3 * IT + k4 * IT**2

                # fCO2 (at in situ T, S, P)
                k0 =  -509.21362402606
                k1 = 0.0114278160526534
                k2 = -8.26788164715874
                k3 = 669.154716801633
                k4 = -62.1641436081941
                k5 = 1.85019546659166
                df['fCO2'] = k0 + k1 * (df['DO (umol/kg)'])**2 + k2 * df['DO (umol/kg)'] + k3 * IT + k4 * IT**2 + k5 * IT**3

                # convert unit from umol/kg to uM
                df['DIC (uM)'] = df['DIC (umol/kg)'] * rho /1000
                df['TA (uM)'] = df['TA (umol/kg)'] * rho /1000

                # Keep only selected columns.
                cols = ['time', 'lat', 'lon', 'z', 'CT', 'PT','SA','SP', 'DO (uM)', 'DIC (uM)', 'TA (uM)', 'pCO2', 'pH', 'OmA']
                this_cols = [item for item in cols if item in df.columns]
                df = df[this_cols]
                # average the df to hourly, to netcdf file
                df.set_index('time', inplace=True)
                df1 = df.resample('h').mean()
                df1.reset_index(inplace=True)
                name = np.repeat(sn, len(df1['time']))
                df1['name'] = name
                column_order = ['time', 'lat', 'lon', 'name', 'z', 'CT', 'PT','SA','SP', 'DO (uM)', 'DIC (uM)', 'TA (uM)', 'pCO2', 'pH', 'OmA']
                df1 = df1[column_order]
                ds = xr.Dataset.from_dataframe(df1)
                ds.to_netcdf(out_fn)
                print(out_fn)

print('Total time = %d sec' % (int(Time()-tt0)))