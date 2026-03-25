"""
code to process the NH10 mooring dataset from 1997-2021 compiled by Craig Risien at OSU

"""

import xarray as xr
import numpy as np
import gsw

from lo_tools import Lfun
Ldir = Lfun.Lstart()


# input location
source = 'NHL'
otype = 'moor'
in_dir = Ldir['data'] / 'obs' / source / otype

# output location
out_dir = Ldir['LOo'] / 'obs' / source / otype

Lfun.make_dir(out_dir,clean = True)


in_fn = in_dir / 'nh10_hourly_data_1997_2021.nc'
moor = xr.open_dataset(in_fn)
out_fn = out_dir / ('NH10' + '_hourly_1997_2021.nc')

# Extract the variables
SP = moor.salinity.values
IT = moor.temperature.values
z = moor.depth.values
lat = moor.latitude.values
lon = moor.longitude.values - 360
p = gsw.p_from_z(-z, lat)

# Initialize the arrays with the correct shape
SA = np.empty_like(SP)
CT = np.empty_like(SP)
PT = np.empty_like(SP)

# Loop through the depth dimension
for i in range(SP.shape[2]):
    pressure = np.full(SP.shape[3], p[i])
    SA[:, :, i, :] = gsw.SA_from_SP(SP[:, :, i, :], pressure, lon, lat)
    CT[:, :, i, :] = gsw.CT_from_t(SA[:, :, i, :], IT[:, :, i, :], pressure)
    PT[:, :, i, :] = gsw.pt_from_t(SA[:, :, i, :], IT[:, :, i, :], pressure, 0)

# Print shapes to debug
print("Shape of SA:", SA.shape)
print("Shape of SP:", SP.shape)
print("Shape of CT:", CT.shape)
print("Shape of PT:", PT.shape)

# Create new DataArrays for SA, CT, and PT with correct dimensions and coordinates
SA_da = xr.DataArray(SA, coords={'longitude': moor.longitude, 'latitude': moor.latitude, 'depth': moor.depth, 'time': moor.time}, dims=['longitude', 'latitude', 'depth', 'time'], name='SA')
SP_da = xr.DataArray(SP, coords={'longitude': moor.longitude, 'latitude': moor.latitude, 'depth': moor.depth, 'time': moor.time}, dims=['longitude', 'latitude', 'depth', 'time'], name='SP')
CT_da = xr.DataArray(CT, coords={'longitude': moor.longitude, 'latitude': moor.latitude, 'depth': moor.depth, 'time': moor.time}, dims=['longitude', 'latitude', 'depth', 'time'], name='CT')
PT_da = xr.DataArray(PT, coords={'longitude': moor.longitude, 'latitude': moor.latitude, 'depth': moor.depth, 'time': moor.time}, dims=['longitude', 'latitude', 'depth', 'time'], name='PT')

# Print DataArray shapes to debug
print("SA_da shape:", SA_da.shape)
print("SP_da shape:", SP_da.shape)
print("CT_da shape:", CT_da.shape)
print("PT_da shape:", PT_da.shape)

# Add the new variables to the dataset
moor['SA'] = SA_da
moor['SP'] = SP_da
moor['CT'] = CT_da
moor['PT'] = PT_da

# Save to NetCDF
moor.to_netcdf(out_fn)