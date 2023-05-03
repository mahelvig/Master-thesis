import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import time
import matplotlib.ticker as ticker
import tqdm

from read_feather import plotting

dir = 'storm_data/Storms/'


def read_feather(fil_dir:str):
    #Function that reads a feather data file and returns it as a dataframe
    df = pd.read_feather(fil_dir)
    df['Timestamp2'] = df['Timestamp']
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df.set_index('Timestamp2', inplace=True)
    
    # Masking where ion mass is manually set to -1
    df = df.mask(df['M_i_eff']==-1)

    return df


def orbit_cutter(df):
    #Function that takes df(with the column 'Latitude') and creates a column with the different orbits

    # Create a new column and stores zeros in it
    df['Orbit_number'] = 0
    #Find where the orbit crosses equator
    #Get latitude values to numpy array
    a = df.Latitude.values
    # Check if two consecutive elements multiplied is a negative number hence changing sign 
    m2 = np.sign(a[1:]*a[:-1])==-1
    # Checking if last element is positive
    m1 = a[:-1]>0 

    r = np.argwhere(np.all(np.vstack([m1,m2]), axis=0))
    sign_index_list = np.squeeze(r)

    # df.loc[df.index[sign_index_list], 'Orbit_number'] = 1
  
    # Define the first orbit as the datapoints before the first crossing of the equator
    df.loc[df.index[:sign_index_list[0]], 'Orbit_number'] = 1
    # Loops through the indecies and adds an orbit number 
    for i, element in enumerate(sign_index_list[:-2]):
        df.loc[df.index[element:sign_index_list[i+1]], 'Orbit_number'] = i+1
    # Define the last orbit as the datapoints after the last crossing of the equator 
    else: 
        df.loc[df.index[sign_index_list[i+1]:], 'Orbit_number'] = i+2

    return df

def conditions(df, start_timestamp, end_timestamp, QDLat_cond = 15, dayside =None,):
    if dayside == True:
        cond_day = (df['MLT'] >= 8) & (df['MLT'] <= 16)
    elif dayside == False:
        cond_day = (df['MLT'] >= 20) | (df['MLT'] <= 4)
    elif dayside == 'Dawn':
        cond_day = (df['MLT'] > 4) & (df['MLT'] < 8)
    elif dayside == 'Dusk':
        cond_day = (df['MLT'] > 16) & (df['MLT'] < 20)
    
    cond_time   = (df.index >= start_timestamp) & (df.index <= end_timestamp)
    cond_lat    = (df['QDLatitude'] >= -QDLat_cond)   & (df['QDLatitude'] <= QDLat_cond) 
    cond_nominal = (df['M_i_eff_Flags'] >= 0)
    

    df2 = df.loc[(cond_day  & 
                 cond_time &
                 cond_lat &
                 cond_nominal)]
    
    return df2

        
def plot(file_names, dst_min, ax_num, column = 'M_i_eff', dawn_dusk = False):
    #Function that plots +/- 3 days of Dst-minimum 

    delta_time      = 5  # days 
    resample_freq   = 1.5  # hours
    QDLat_cond      = 50  #Degrees

    df_A = read_feather(dir+file_names[0])
    df_B = read_feather(dir+file_names[1])
    df_C = read_feather(dir+file_names[2])
    # Adds the orbits
    df_A = orbit_cutter(df_A)
    df_B = orbit_cutter(df_B)
    df_C = orbit_cutter(df_C)

    # print(df_A)

    # specify the dst minmum timestamp
    dst_min = pd.Timestamp(dst_min)

    # Select the rows within +/- three days of the Dst minimum timestamp 
    # and at equatorial dayside region
    start_timestamp = dst_min - pd.Timedelta(days=delta_time)
    end_timestamp   = dst_min + pd.Timedelta(days=delta_time)

    
    df_A_2          = conditions(df_A, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                        QDLat_cond=QDLat_cond, dayside=('Dawn' if dawn_dusk else True))
    df_B_2          = conditions(df_B, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                        QDLat_cond=QDLat_cond, dayside=True)
    df_C_2          = conditions(df_C, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                        QDLat_cond=QDLat_cond, dayside=('Dawn' if dawn_dusk else True))
    
    df_A_2_night    = conditions(df_A, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                        QDLat_cond=QDLat_cond, dayside=('Dusk' if dawn_dusk else False))
    df_B_2_night    = conditions(df_B, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                        QDLat_cond=QDLat_cond, dayside=False)
    df_C_2_night    = conditions(df_C, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                        QDLat_cond=QDLat_cond, dayside=('Dusk' if dawn_dusk else False))
    
    
    df_A_resampled      = df_A_2.groupby('Orbit_number')[['M_i_eff','Timestamp','M_i_eff_tbt_model' ]].median(numeric_only=False)
    df_B_resampled      = df_B_2.groupby('Orbit_number')[['M_i_eff','Timestamp','M_i_eff_tbt_model' ]].median(numeric_only=False)
    df_C_resampled      = df_C_2.groupby('Orbit_number')[['M_i_eff','Timestamp','M_i_eff_tbt_model' ]].median(numeric_only=False)
    df_A__night_resampled      = df_A_2_night.groupby('Orbit_number')[['M_i_eff','Timestamp','M_i_eff_tbt_model' ]].median(numeric_only=False)
    df_B__night_resampled      = df_B_2_night.groupby('Orbit_number')[['M_i_eff','Timestamp','M_i_eff_tbt_model' ]].median(numeric_only=False)
    df_C__night_resampled      = df_C_2_night.groupby('Orbit_number')[['M_i_eff','Timestamp','M_i_eff_tbt_model' ]].median(numeric_only=False)
    

    # Plotting
    ax[(0,0)].plot(df_A_resampled['Timestamp'],df_A_resampled['M_i_eff'], color = 'tab:blue',  label = f'SWARM A')
    ax[(1,0)].plot(df_B_resampled['Timestamp'],df_B_resampled['M_i_eff'], color = 'tab:red',   label = f'SWARM B')
    ax[(2,0)].plot(df_C_resampled['Timestamp'],df_C_resampled['M_i_eff'], color = 'tab:green', label = f'SWARM C')

    ax[(0,1)].plot(df_A__night_resampled['Timestamp'],df_A__night_resampled['M_i_eff'], color = 'tab:blue',  label = f'SWARM A')
    ax[(1,1)].plot(df_B__night_resampled['Timestamp'],df_B__night_resampled['M_i_eff'], color = 'tab:red',   label = f'SWARM B')
    ax[(2,1)].plot(df_C__night_resampled['Timestamp'],df_C__night_resampled['M_i_eff'], color = 'tab:green', label = f'SWARM C')

    #Plotting IRI 2016
    ax[(0,0)].plot(df_A_resampled['Timestamp'],df_A_resampled['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')
    ax[(1,0)].plot(df_B_resampled['Timestamp'],df_B_resampled['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')
    ax[(2,0)].plot(df_C_resampled['Timestamp'],df_C_resampled['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')
    ax[(0,1)].plot(df_A__night_resampled['Timestamp'],df_A__night_resampled['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')
    ax[(1,1)].plot(df_B__night_resampled['Timestamp'],df_B__night_resampled['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')
    ax[(2,1)].plot(df_C__night_resampled['Timestamp'],df_C__night_resampled['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')

    storm_name = ['June 2015', 'December 2015', 'September 2017', 'August 2018']
    

    for j in range(2):
        for i in range(3):
            ax[(i,j)].set_ylabel(r'Effective Ion Mass [u]')
            ax[(i,j)].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
            ax[(i,j)].legend(loc = 'lower right')
            ax[(i,j)].axhline(y = 16, color = 'black', ls = '--',linewidth=1)
            ax[(i,j)].axvline(x = dst_min, color = 'black', ls = '--',linewidth=1)
            ax[(i,j)].set_xlim(start_timestamp, end_timestamp)
            ax[(i,0)].set_title(f'Dayside')
            ax[(i,1)].set_title(f'Nightside')
            # ax[(i,j)].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)
    
    if dawn_dusk:
        ax[(0,0)].set_title(f'Dawnside')
        ax[(1,0)].set_title(f'Dayside')
        ax[(2,0)].set_title(f'Dawnside')
        ax[(0,1)].set_title(f'Duskside')
        ax[(1,1)].set_title(f'Nightside')
        ax[(2,1)].set_title(f'Duskside')



    # ax[(0,0)].set_title(f'Dayside')
    # ax[(0,1)].set_title(f'Nightside')
    
    # fig.legend(('SWARM A','SWARM B','SWARM C'),loc='center', bbox_to_anchor=(0.78, 0.52), ncol=3)

    # plt.xlabel('Orbit number')
    plt.suptitle(f'Median Effective Ion Mass per Orbit at {storm_name[ax_num]} Storm ')
    # plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(f'storm_data/Plots/Median Ion Mass per orbit at {storm_name[ax_num]} storm.png')
    # plt.show()


if __name__ == '__main__':
    # Storm data file names
    june_A      = '2015_06_sat_A'
    june_B      = '2015_06_sat_B'
    june_C      = '2015_06_sat_C'
    december_A  = '2015_12_sat_A'
    december_B  = '2015_12_sat_B'
    december_C  = '2015_12_sat_C'
    september_A = '2017_09_sat_A'
    september_B = '2017_09_sat_B'
    september_C = '2017_09_sat_C'
    august_A    = '2018_08_sat_A'
    august_B    = '2018_08_sat_B'
    august_C    = '2018_08_sat_C'

    june_dst_min        = '2015-06-23 04:24:00'
    december_dst_min    = '2015-12-20 22:49:00'
    september_dst_min   = '2017-09-08 01:08:00'
    august_dst_min      = '2018-08-26 07:11:00'

    june_file_names     = ['2015_06_sat_A','2015_06_sat_B','2015_06_sat_C']
    december_file_names = ['2015_12_sat_A','2015_12_sat_B','2015_12_sat_C']
    september_file_names= ['2017_09_sat_A','2017_09_sat_B','2017_09_sat_C']
    august_file_names   = ['2018_08_sat_A','2018_08_sat_B','2018_08_sat_C']

    name_list = [june_file_names,december_file_names,september_file_names,august_file_names]


    for i, element in enumerate([june_dst_min, december_dst_min, september_dst_min, august_dst_min]):
        fig, ax = plt.subplots(3,2,figsize=(25,15))#sharex=True,) 
        # If statement to make sure dawn/dusk for December storm is included
        if i == 1:
            plot(file_names=name_list[i], dst_min=element, ax_num = i, column = 'M_i_eff', dawn_dusk = True)        
        else:
            plot(file_names=name_list[i], dst_min=element, ax_num = i, column = 'M_i_eff')
        # plt.show()

