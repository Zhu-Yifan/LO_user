"""
Plot all bottle data to check on patterns and gaps.
"""
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from lo_tools import plotting_functions as pfun
from lo_tools import Lfun, zfun, zrfun
Ldir = Lfun.Lstart()

source = 'nceiCoastal'
otype = 'bottle'
year = 2017
small = True

out_dir = Ldir['LOo'] / 'obs' / source / otype
ys = str(year)
fn = out_dir / (ys + '.p')
info_fn = out_dir / ('info_' + ys + '.p')

out_dir0 = Ldir['LOo'] / 'plots' / 'obs' / source 


obs_df = pd.read_pickle(fn)
info_df = pd.read_pickle(info_fn)

if small:
    pfun.start_plot(fs=11)
    fig = plt.figure(figsize=(12,8)) # laptop size
else:
    pfun.start_plot(figsize=(20,12), fs=12)
    
plt.close('all')


# sequences of stations
sta_list_p = ['P28', 'P6','P21','P136','P133','P131','P123','P120']
sta_list_lab = ['LAB10', 'LAB08', 'LAB06', 'LAB04', 'LAB02']
sta_list_nm = ['NM01', 'NM02','NM04','NM06','NM08']
sta_list_kb = ['KB06', 'KB04','KB03','KB02','KB01']
sta_list_gr = ['GR01', 'GR03','GR05','GR07','GR09']
sta_list_cr = ['CR01', 'CR02','CR03','CR05','CR07']
sta_list_cm = ['CM01', 'CM02','CM03','CM05','CM07']
sta_list_NHL = ['NH01', 'NH05', 'NH15', 'NH25', 'NH45', 'NH85', 'NH125']
sta_list_hb = ['HB01', 'HB02','HB03','HB04','HB0405','HB0407']

# legend size
#leg_dict = {'NO3 (uM)':25, 'DIN (uM)':25, 'NH4 (uM)':2, 'DO (uM)': 300}
leg_dict = {'NO3 (uM)':25, 'DIN (uM)':25, 'DIC (uM)':2000, 'DO (uM)': 300}
fac_dict = {}
for vn in leg_dict.keys():
    fac_dict[vn] = 10/leg_dict[vn]
    
obs_df['DIN (uM)'] = obs_df['NO3 (uM)'] + obs_df['NH4 (uM)']

# get time information, specifically the month of each cruise
cruise_list = list(obs_df.cruise.unique())
date_list = []
for cruise in cruise_list:
    date_list.append(obs_df.loc[obs_df.cruise==cruise,'time'].iloc[0])
cruise_dict = dict(zip(date_list, cruise_list))
date_list.sort()

for vn in leg_dict.keys():
    fig = plt.figure()

    do_legend=True
    cc = 0
    for this_date in date_list:
        cruise = cruise_dict[this_date]
        ax = plt.subplot2grid((3,3), (cc,0), colspan=2)
        if cc == 0:
            ax.set_title('%s  (%s)' % (vn, year))
        ii = 0
        for sn in  sta_list_p + sta_list_lab + sta_list_nm + sta_list_kb + sta_list_gr + sta_list_cr + sta_list_cm + sta_list_NHL + sta_list_hb:
            o = obs_df.loc[(obs_df.cruise==cruise) & (obs_df.name==sn), vn].to_numpy()
            oz = obs_df.loc[(obs_df.cruise==cruise) & (obs_df.name==sn), 'z'].to_numpy()
            for jj in range(len(o)):
                O = o[jj]
                Z = oz[jj]
        
                # plot data
                if np.isnan(O):
                    ax.plot(ii,Z,'+k')
                else:
                    ax.plot(ii,Z, marker='o', ls='', ms=fac_dict[vn]*O, c='r', alpha=.3)
        
                # add a legend
                if (sn == sta_list_p[0]) and (cc==0) and do_legend:
                    ax.plot(ii+.5,-550, marker='o', ls='',
                        ms=fac_dict[vn]*leg_dict[vn],
                        c='r', alpha=.3)
                    ax.text(ii+1,-550,'%s = %d' % (vn, leg_dict[vn]), c = 'r',
                        fontweight='bold', va='center', alpha=.5)
                    do_legend = False
            
            ax.set_ylabel('Z (m)')
    
            # add a vertical line between station sequences
            if sn in [sta_list_p[-1],
                      sta_list_lab[-1],  
                      sta_list_nm[-1], 
                      sta_list_kb[-1], 
                      sta_list_gr[-1], 
                      sta_list_cr[-1], 
                      sta_list_cm[-1],
                      sta_list_NHL[-1],                      
                      sta_list_hb[-1]]:
                ax.axvline(ii+.5)
    
            # add station labels
            if cc == 0:
                if sn in sta_list_NHL:
                    sn_c = 'm'
                elif sn in sta_list_lab:
                    sn_c = 'c'
                elif sn in sta_list_p:
                    sn_c = 'g'
                elif sn in sta_list_nm:
                    sn_c = 'r'    
                elif sn in sta_list_kb:
                    sn_c = 'k'   
                elif sn in sta_list_gr:
                    sn_c = 'b'
                elif sn in sta_list_cr:
                    sn_c = 'pink'
                elif sn in sta_list_cm:
                    sn_c = 'gray'
                elif sn in sta_list_hb:
                    sn_c = 'orange'
                ax.text(ii,-250,sn,ha='center',va='center',rotation=60,style='italic',c=sn_c)
                ax.set_xlabel('Station')
        
            # add month info
            ax.text(.025,.2, 'Month = %d' % (this_date.month), fontweight='bold',
                transform=ax.transAxes)
        
            ii += 1
        cc += 1
        ax.set_xlim(-1,50)
        ax.set_ylim(-600,25)
        ax.set_xticks([])

    # add a map
    # Load the processed file
    cruise = cruise_list[0]
    x = info_df.loc[info_df.cruise==cruise,'lon'].to_numpy()
    y = info_df.loc[info_df.cruise==cruise,'lat'].to_numpy()
    #sn = [int(item) for item in info_df.loc[info_df.cruise==cruise,'name'].to_numpy()]
    sn = info_df.loc[info_df.cruise == cruise, 'name'].to_numpy()
    ax = fig.add_subplot(1,3,3)
    for ii in range(len(x)):
        if sn[ii] in sta_list_NHL:
            sn_c = 'm'
        elif sn[ii] in sta_list_lab:
            sn_c = 'c'
        elif sn[ii] in sta_list_p:
            sn_c = 'g'
        elif sn[ii] in sta_list_nm:
            sn_c = 'r'    
        elif sn[ii] in sta_list_kb:
            sn_c = 'k'   
        elif sn[ii] in sta_list_gr:
            sn_c = 'b'
        elif sn[ii] in sta_list_cr:
            sn_c = 'pink'
        elif sn[ii] in sta_list_cm:
            sn_c = 'gray'
        elif sn[ii] in sta_list_hb:
            sn_c = 'orange'
        ax.plot(x[ii],y[ii],marker='o',c=sn_c)
        ax.text(x[ii]+.06,y[ii],str(sn[ii]),c=sn_c,
            ha='center',va='center',rotation=60,style='italic')
        #ax.text(x[ii]+.06,y[ii],sn[ii],c=sn_c,
        #    ha='center',va='center',rotation=60,style='italic')
    pfun.dar(ax)
    pfun.add_coast(ax, color='gray')
    ax.axis([-130, -122, 42, 52])
    ax.set_xticks([])
    ax.set_yticks([])
    ff_str = f'{otype}_{year}_{source}_{vn}_obs'
    plt.savefig(out_dir0 / (ff_str + '.png'))

plt.show()

    
