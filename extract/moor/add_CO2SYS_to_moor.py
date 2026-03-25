"""
Code to add CO2sys parameters to the extracted .nc file
"""

import numpy as np
import xarray as xr
import gsw
import PyCO2SYS as pyco2
from lo_tools import Lfun
Ldir = Lfun.Lstart()

# input location
type = 'moor'
fod1 = 'LineP'
fod2 = 'monthly'
gtx = 'cas2k_v4_x2b'
in_dir = Ldir['LOo'] / 'extract'/ gtx / type / fod1/ fod2
# output location
out_dir = in_dir / 'CO2SYS'
Lfun.make_dir(out_dir, clean=False)

testing = False
if testing:
    year_list = [2009]
else:
    year_list = np.arange(1993,2023)

if fod1 == 'LineP':
    sn_list = [
        'P04',
        'P12',
    ]


# Define file paths
for sn in sn_list:
    print(sn)
    fn = str(in_dir/f'{sn}_{year_list[0]}.01.01_{year_list[-1]}.12.31.nc')
    ds = xr.open_dataset(fn)
    # Read variables from the NetCDF file
    varT = ds['temp'].values
    varS = ds['salt'].values
    varTIC = ds['TIC'].values
    varALK = ds['alkalinity'].values
    varNH4 = ds['NH4'].values
    varDO = ds['oxygen'].values
    varNO3 = ds['NO3'].values
    z = ds['z_w'].values
    lat = ds['lat_rho'].values * np.ones_like(z)
    lon = ds['lon_rho'].values * np.ones_like(z)

    Lpres = gsw.p_from_z(z[:, 1:], lat[:, 1:]) # pressure [dbar]

    SA = gsw.SA_from_SP(varS, Lpres, lon[:, 1:], lat[:, 1:])
    CT = gsw.CT_from_pt(SA, varT)
    rho = gsw.rho(SA, CT, Lpres) # in situ density
    Ltemp = gsw.t_from_CT(SA, CT, Lpres) # in situ temperature
    # convert from umol/L to umol/kg using in situ density
    Lalkalinity = 1000 * varALK / rho
    Lalkalinity[Lalkalinity < 100] = np.nan
    LTIC = 1000 * varTIC / rho
    LTIC[LTIC < 100] = np.nan

    LNH4 = 1000 * varNH4 / rho
    LNH4[LNH4 < 0] = np.nan

    LDO = 1000 * varDO / rho
    LDO[LDO < 0] = np.nan

    LNO3 = 1000 * varNO3 / rho
    LNO3[LNO3 < 0] = np.nan

    ds['TIC'] = xr.DataArray(LTIC, dims=('ocean_time', 's_rho'))  # in umol/kg unit
    ds['alkalinity'] = xr.DataArray(Lalkalinity, dims=('ocean_time', 's_rho')) # in umol/kg unit
    ds['oxygen'] = xr.DataArray(LDO, dims=('ocean_time', 's_rho')) # in umol/kg unit
    ds['NO3'] = xr.DataArray(LNO3, dims=('ocean_time', 's_rho')) # in umol/kg unit
    # Define input conditions
    kwargs = dict(
        par1 = Lalkalinity,  # Value of the first parameter, unit: umol/kg
        par2 = LTIC,  # Value of the second parameter, which is a long vector of different DIC's! unit: umol/kg
        par1_type = 1 ,  # The first parameter supplied is of type "1", which is "alkalinity"
        par2_type = 2,  # The second parameter supplied is of type "2", which is "DIC"
        salinity = varS,  # Salinity of the sample
        temperature = Ltemp,  # Temperature at input conditions; in situ temperature
        pressure = Lpres,        # # lab pressure (input conditions) in dbar, ignoring the atmosphere
        total_silicate = 50,  # Concentration of silicate in the sample (in umol/kg)
        total_phosphate = 2,  # Concentration of phosphate in the sample (in umol/kg)
        total_ammonia = LNH4,  # total ammonia in μmol/kg-sw
        total_sulfide = 0.0,  # total sulfide in μmol/kg-sw
        opt_pH_scale = 1,     # tell PyCO2SYS: "the pH input is on the Total scale"
        opt_k_carbonic = 7,  # Choice of H2CO3 and HCO3- dissociation constants K1 and K2 ("7" means the carbonic acid dissociation constants of Mehrbach et al.1973;
                             # without certain species aka "Peng" (2 < T < 35 °C, 19 < S < 43, NBS scale, real seawater)
                             # This has to be consistent with the LiveOcean parameterization too
        opt_k_bisulfate = 1,  # Choice of HSO4- dissociation constants KSO4 ("1" means "Dickson 1990), it is consistent with LO_parameterization
        opt_total_borate = 1,  # tell PyCO2SYS: "use borate:salinity of U74". It is consistent with LO_parameterization
        opt_k_fluoride = 1, # Choice of HF dissociation constants: ("1" means "Dickson and Riley 1979). it is consistent with LO_parameterization
    )
    print("Input conditions have been set!")

    # Run CO2SYS
    CO2dict = pyco2.sys(**kwargs)
    print('PyCO2SYS ran successfully!')

    # Extract the calculated variables
    varARAG = CO2dict['saturation_aragonite']
    varpH = CO2dict['pH']
    varpCO2 = CO2dict['pCO2']
    varfCO2 = CO2dict['fCO2']
    # Create xarray DataArrays for the calculated variables
    arag_da = xr.DataArray(varARAG, dims=('ocean_time', 's_rho'))
    ph_da = xr.DataArray(varpH, dims=('ocean_time', 's_rho'))
    pco2_da = xr.DataArray(varpCO2, dims=('ocean_time', 's_rho'))
    fco2_da = xr.DataArray(varfCO2, dims=('ocean_time', 's_rho'))


    # Add these variables to the existing xarray Dataset
    ds['OmA'] = arag_da
    ds['pH'] = ph_da
    ds['pCO2'] = pco2_da
    ds['fCO2'] = fco2_da
    # Save the modified dataset back to the NetCDF file
    ds.to_netcdf(f"{out_dir}/{sn}_{year_list[0]}.01.01_{year_list[-1]}.12.31_CO2SYS.nc", mode='w', format='NETCDF4')
    print(f'CO2SYS data is saved for {sn}')
    # Close the dataset
    ds.close()


