import numpy as np
import glob
from mhw_utilities import *
import matplotlib.pyplot as plt
from statistics import NormalDist  # I think python 3.5 and geater is needed here...
import os.path
import calendar

from lo_tools import Lfun

# See the following for documentation of this climatatology data...
# The 1991–2020 sea surface temperature normals, Xungang Yin et al., (2023)
# Data download here: https://www.ncei.noaa.gov/data/oceans/archive/arc0229/0282469/1.1/data/0-data/


# ---
Ldir = Lfun.Lstart()

in_dir = Ldir['LOu'] / 'extract'/ 'stressor'/ 'MHW'/'data' 

if not os.path.exists(in_dir):
    os.makedirs(in_dir)
    
fname_clim= os.path.expanduser(f'{in_dir}/1991-2020-SST_Normals-Daily_mean-std-001.nc')

folder = 'oisst-2014' # OISST daily .nc file in year 2014
fname_list= glob.glob(os.path.expanduser(f'{in_dir}/{folder}/*.nc'))
fname_list=np.sort(fname_list)  # Note: glob.glob on its own does not retrun a sorted list...

# --------------------------------------------------------------------------------------

# Geographic point of intest for time series extraction
# ---
lat= 47.0
lon=-125.0



# oisst file details...
# ---
nrows=720
ncols=1440

west_lon=-180
east_lon=+180
north_lat=90
south_lat=-90

# Convert geographic location from lat-lon to row-column
# ---
icol= int(round((180+lon)*(ncols-1)/(east_lon-west_lon)))
irow= int(round((90-lat)*(nrows-1)/(north_lat-south_lat)))


# --------------------------------------------------------------------------------------

# Read in daily climatology data from netcdf file...
# ---
print('\nreading daily climatology norms and stdevs (note: this is a big file)...\n')
clim_oisst_mean=  read_cdf_prod(fname_clim, 'norm')*1.0
clim_oisst_stdev= read_cdf_prod(fname_clim, 'std')*1.0
clim_oisst_jday=  read_cdf_prod(fname_clim, 'time')*1.0

clim_oisst_mean=np.flip(clim_oisst_mean,axis=1)           #flip north/south
clim_oisst_mean=np.roll(clim_oisst_mean,720,axis=2)       #change lon from (0 to 360) ---> (-180 to +180)
fill_locations= np.where(clim_oisst_mean == -999.9)       #change missing data flag from -999.9 to NaN
clim_oisst_mean[fill_locations]= np.nan

clim_oisst_stdev=np.flip(clim_oisst_stdev,axis=1)         #flip north/south
clim_oisst_stdev=np.roll(clim_oisst_stdev,720,axis=2)     #change lon from (0 to 360) ---> (-180 to +180)
fill_locations= np.where(clim_oisst_stdev == -999.9)      #change missing data flag from -999.9 to NaN
clim_oisst_stdev[fill_locations]= np.nan


# Extract time series for the specified geographic location...
# ---
clim_oisst_mean_location= clim_oisst_mean[:,irow,icol]
clim_oisst_stdev_location= clim_oisst_stdev[:,irow,icol]

# Compute the sst value representing the 90th percentile for the specified geographic location...
# ---
clim_oisst_90quantile_value_location=np.zeros(len(clim_oisst_mean_location))
for i in range(len(clim_oisst_mean_location)):
    clim_oisst_90quantile_value_location[i]= NormalDist(mu=clim_oisst_mean_location[i], sigma=clim_oisst_stdev_location[i]).inv_cdf(0.90)

# The climatology seriies has 366 days (i.e., includes leap year (Feb 29).
# Analysing a daily sst series that does not have a leap year, then remove
# Feb 29 (jday 60) from the climatology and shoten to 365 days.

#calendar.isleap(1900)

sst_basename=os.path.basename(fname_list[0])
splt_name= sst_basename.split('.')
sst_year= int(splt_name[1][0:4])

if calendar.isleap(sst_year) == False:
    shortened_clim_sst= []
    shortened_clim_90quantile= []

    for i in range(len(clim_oisst_mean_location)):
        if i != 59:                                                  #jday[index=59]=60
            shortened_clim_sst.append(clim_oisst_mean_location[i])
            shortened_clim_90quantile.append(clim_oisst_90quantile_value_location[i])
    julian_day=np.linspace(1,365,365)
else:
    shortened_clim_sst=  clim_oisst_mean_location
    shortened_clim_90quantile=clim_oisst_90quantile_value_location
    julian_day=np.linspace(1,366,366)


# --------------------------------------------------------------------------------------

# Read in daily sst data for a given year from netcdf files and xtract sst value at
# the specified geographic location to build time series day by dday with each time through the loop.
# ---
year_oisst_series= []
for fname in fname_list:
    sst_basename=os.path.basename(fname)
    print('reading sst data from file: ', sst_basename)
    year_oisst= read_cdf_prod(fname, 'sst').squeeze()*.01   #0.01 is scale factor give in the file meta data for sst

    year_oisst=np.flip(year_oisst,axis=0)                   #flip north/south
    year_oisst=np.roll(year_oisst,720, axis=1)              #change lon from (0 to 360) ---> (-180 to +180)

    year_oisst_series.append(year_oisst[irow,icol])



# Plot all three time series on a single figure
# ---
plt.figure('sst time series')
plt.plot(julian_day,shortened_clim_sst,  label='climatology')
plt.plot(julian_day,shortened_clim_90quantile,  label='90th Precentile')
plt.plot(julian_day,year_oisst_series,  label=sst_year)
plt.legend(loc='upper left')
plt.xlabel('julian day')
plt.ylabel('sea surface temperature')
plt.title('sst time series for lat= ' + str(lat) + ' and lon= ' + str(lon))
plt.show()
