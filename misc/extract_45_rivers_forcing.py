"""
This is a script to extract historical river forcing from LiveOcean.
"""

import numpy as np
import xarray as xr
import pandas as pd
import os
import calendar
from lo_tools import Lfun
Ldir = Lfun.Lstart()

out_dir = Ldir['LOo'] / 'forcing' / 'cas2k' / 'river'
Lfun.make_dir(out_dir)

river = True
if river:
    fn_dir = '/a1/fsoares/LiveOcean/LO_output/forcing/cas2k'
    sub_folder = 'riv00'
    source_file_name = 'rivers.nc'
    year_list = np.arange(1993, 2022+1)
    month_list = np.arange(1, 13)
    fn_list = []
    ds_list = []
    for year in year_list:
        print(year)
        for month in month_list:
            print(month)
            # Get the number of days in the month
            _, days = calendar.monthrange(int(year), month)
            day_list = np.arange(1, days + 1)
            for day in day_list:
                print(day)
                folder = f'f{year}.{month:02d}.{day:02d}'
                print(folder)
                # Construct the source file path
                fn = os.path.join(fn_dir,folder,sub_folder, source_file_name)
                # fn_list.append(fn)
                df = xr.open_dataset(fn)
                vn = ['river_direction','river_transport']
                ds = df[vn].sel(river_time=pd.to_datetime(f'{year}-{month:02d}-{day:02d} 12:00:00'))
                df.close()
                ds_list.append(ds)
    ds = xr.concat(ds_list, dim='river_time')
    print('finished all the files')
    ds.to_netcdf(f'{out_dir}/river_historical_{year_list[0]}-{year_list[-1]}.nc')
    print(f'extract river forcing is saved')