import numpy as np
import glob
import matplotlib.pyplot as plt
from subprocess import call
from subprocess import run
from datetime import date, timedelta
import os.path
from lo_tools import Lfun

Ldir = Lfun.Lstart()

# -----------------------------------------------------------------------------------
def wget_ncei_oisst(year):
# -----------------------------------------------------------------------------------
    """
    Downloads daily OISST daily data for a specified year and saves it to the given directory.
    
    Parameters:
    year (int): The year of the data to download.
    save_dir (str): The directory where downloaded files will be saved.
    """
    # Ensure the save directory exists
    
    folder = f'oisst-{year}'
    out_dir = Ldir['data'] / 'climatology'/ 'OISST'/ folder 
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    import re
    import requests

    year= str(year)
    mon_list= ['01','02','03','04','05','06','07','08','09','10','11','12']


    for mon in mon_list:
        oisst_dir='https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/' + year + mon + '/'
        result= requests.get(oisst_dir).text
        clean= re.compile('<.*?>')
        clean_result= re.sub(clean,'', result).split(';')  # still has a bunch of trailing grabage after .nc

        for name in clean_result:
            print(name)
            match= re.search('.nc', name)
            if match != None:
                name_only= name[0:match.start()+3].strip('\n')
                if year+mon in name_only:
                    file_url = oisst_dir + name_only
                    print(f'Downloading {file_url}')
                    #print(oisst_dir + name_only)
                wget_command = [
                      'wget',
                      'load-cookies=' + '~/.urs_cookies',
                      'save-cookies=' + '~/.urs_cookies',
                      '--auth-no-challenge=on',
                      '--keep-session-cookies',
                      '--no-check-certificate',
                      '--directory-prefix=' + str(out_dir),
                      file_url
                      
                      ]
                      
                call(wget_command)



# -----------------------------------------------------------------------------------
def download_ghrsst_subscene(start_yyymmdd, end_yyyymmdd, n,s,e,w):
# -----------------------------------------------------------------------------------
# This utility pulls over subscened GHRSST data for a specified date range and geographic bounds
#
# NOTE: before using this function, you must install the python package: podaac-data-subscriber
# as of 7/22/2024 conda install retrievs an older version.  It was suggested by podaac to use
# the pip installer methods.  pip install podaac-data-subscriber
# example call from unix for gulf of maine:
# podaac-data-downloader -c MUR-JPL-L4-GLOB-v4.1 -d ./ --start-date 2003-01-01T09:00:00Z --end-date 2003-01-03T09:00:00Z  -b="-72,37,-63,46" --subset

# NOTE:  You will lilely need to be a registered user with earthdata (https://www.earthdata.nasa.gov) and have your user name and password added
# to your  ~/.netrc file.
# ---

    syear=start_yyymmdd[0:4]
    smon=start_yyymmdd[4:6]
    sday=start_yyymmdd[6:8]
    sd= syear + '-' + smon + '-' + sday + 'T00:00:00Z'

    eyear=end_yyyymmdd[0:4]
    emon=end_yyyymmdd[4:6]
    eday=end_yyyymmdd[6:8]
    ed= eyear + '-' + emon + '-' + eday + 'T00:00:00Z'

    lat_lon_bounds= w + ',' + s + ',' + e + ',' + n

    call(['podaac-data-downloader',
          '-c', 'MUR-JPL-L4-GLOB-v4.1',
          '-d', './',
          '--start-date=' + sd,
          '--end-date='   + ed,
          '-b= ' + lat_lon_bounds,
          '--subset',])



# -----------------------------------------------------------------------------------
def read_cdf_prod(ifile,prod):
# -----------------------------------------------------------------------------------
# This utility reads in specified products (e.g,, sst) from a specified netcdf file.

    from netCDF4 import Dataset

    f = Dataset(os.path.expanduser(ifile), 'r')

    f.set_auto_maskandscale(False)  # NOTE: setting this to False turnes OFF the automatic (on the fly) application of scale_factor and off_set when netdcf4 data are read
                                            # scale_factor and off_set when netdcf4 data are read in.  This was done to ensure consistent application of slope intercerpt
                                            # which now will have to be done manually after reading things into the main program not matter how the netcdf data were written out.

    group_names= list(f.groups.keys())  #get group names (e.g. geophtsical_data_sets or navigation)

    if len(group_names) != 0:
        #if smi format has one group called 'processing_control', but the variables at top level (under no group) so read as if no groups
        if group_names[0] == 'processing_control':

            p =  f.variables[prod]
            if len(p.shape) == 1:data=  p[:]
            if len(p.shape) == 2:data=  p[:,:]
            if len(p.shape) == 3:data=  p[:,:,:]
            if len(p.shape) == 4:data=  p[:,:,:,:]

            f.close()
            return data


        #for all other regular l2 netcdf4 files with groups and varibles under groups
        else:

            for grp_name in group_names:
                var_name= list(f.groups[grp_name].variables.keys())  #get names of objects within each group (e,g. chlor_a or longitude)
                for vn in var_name:
                    if vn == prod:

                        p =  f.groups[grp_name].variables[vn]
                        if len(p.shape) == 1:data=  p[:]
                        if len(p.shape) == 2:data=  p[:,:]
                        if len(p.shape) == 3:data=  p[:,:,:]
                        if len(p.shape) == 4:data=  p[:,:,:,:]

                        f.close()
                        return data

    # netcdf4 file has NO groups so variable are at top level and not under a group...
    else:
        var_name= list(f.variables.keys())

        p =  f.variables[prod]
        if len(p.shape) == 1:data=  p[:]
        if len(p.shape) == 2:data=  p[:,:]
        if len(p.shape) == 3:data=  p[:,:,:]
        if len(p.shape) == 4:data=  p[:,:,:,:]

        f.close()
        return data.squeeze()



# -----------------------------------------------------------------------------------
def read_daily_ncei_oisst_dates(ifile):
# -----------------------------------------------------------------------------------
# This utility is used by the function below (image_daily_oisst_anomaly).
# It reads the 'time' product from a daily oisst file and retruns a julian day.
# NOTE: daily oisst 'time' product is defined as "days since 1978-01-01 12:00:00"

    start_day= date(1978,1,1)
    elapsed_days= read_cdf_prod(ifile,'time').squeeze()
    delta = timedelta(days=int(elapsed_days))
    data_date = start_day + delta
    tt = data_date.timetuple()
    sjday= tt.tm_yday
    return int(sjday)


# -----------------------------------------------------------------------------------
def image_daily_oisst_anomaly(folder,yyyymmdd):
# -----------------------------------------------------------------------------------
# This utility prduces a gloab map of sst anomaly (relative to the 30year climatology) for
# a specified year and day.
    
    in_dir = Ldir['LOu'] / 'extract'/ 'stressor'/ 'MHW'/'data' 
    fname_clim= os.path.expanduser(f'{in_dir}/1991-2020-SST_Normals-Daily_mean-std-001.nc')
    print('\nreading in climatology sst (all days)...')
    clim_oisst_mean= read_cdf_prod(fname_clim,'norm')*1.0
    print('reading in climatology julian day for each sst...')
    clim_jday= read_cdf_prod(fname_clim,'time')

    clim_oisst_mean=np.flip(clim_oisst_mean,axis=1)           #flip north/south
    clim_oisst_mean=np.roll(clim_oisst_mean,720,axis=2)       #change lon from (0 to 360) ---> (-180 to +180)
    fill_locations= np.where(clim_oisst_mean == -999.9)       #change missing data flag from -999.9 to NaN
    clim_oisst_mean[fill_locations]= np.nan


    fname_list= glob.glob(os.path.expanduser(f'{in_dir}/{folder}' + '/*' + yyyymmdd + '*.nc'))
    fname= fname_list[0]
    base_fname= os.path.basename(fname)
    print('\nreading sst for specified year and date using file: ',base_fname)
    daily_oisst_sst= read_cdf_prod(fname,'sst').squeeze()*.01
    daily_oisst_sst=np.flip(daily_oisst_sst,axis=0)
    daily_oisst_sst=np.roll(daily_oisst_sst,720, axis=1)

    daily_oisst_jday= read_daily_ncei_oisst_dates(fname)


    good_clim_jday_index=np.where(clim_jday == daily_oisst_jday)
    good_clim_day_sst= clim_oisst_mean[good_clim_jday_index,:,:].squeeze()

    sst_anomaly= daily_oisst_sst-good_clim_day_sst
    #sst_anomaly=np.roll(sst_anomaly,720, axis=1 )

    mycmap = plt.get_cmap('coolwarm').copy()	 # load color rainbow palette
    mycmap.set_bad('k')			                 # set NaN values to display as black
    plt.figure('sst anomaly')
    plt.imshow(sst_anomaly, cmap=mycmap, vmin=-3,vmax=3)
    plt.colorbar(orientation="horizontal", label='sst anomaly (celsius)')
    plt.title("SST Anomaly for OISST File: " + base_fname)
    plt.show()

# --------------------------------------------------------------------------------------
