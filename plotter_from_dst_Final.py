import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import time
import matplotlib.ticker as ticker
import tqdm
import matplotlib.dates as mdates
from read_feather import plotting

### This program creates the effective ion mass plots for the thesis ###

dir = 'storm_data/Storms/'


def read_feather(fil_dir:str):
    #Function that reads a feather data file and returns it as a dataframe
    df = pd.read_feather(fil_dir)
    df['Timestamp2'] = df['Timestamp']
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df.set_index('Timestamp2', inplace=True)
    
    # Masking where ion mass is manually set to -1
    df = df[df['M_i_eff'] != -1]
    # print(df)

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

def new_orbit_cutter(df):
    # Defines an orbit as when the satellite crosses +70 degrees 

    # calculate the orbit numbers using vectorized operations
    lat = df['Latitude']
    orbit = np.where((lat > 70) & (lat.shift() < 70), 1, 0).cumsum()
    df['Orbit_number'] = orbit
    
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

def check_time_gap(df):
    # calculate the time difference between consecutive timestamps
    time_diff = df['Timestamp'].diff()

    # check if any of the time differences are greater than 12 hours
    has_gap = (time_diff > pd.Timedelta(hours=12)).any()

    # print the result
    if has_gap:
        print("There is a gap in the Timestamp column greater than 12 hours.")
        return True
    else:
        print("There are no gaps in the Timestamp column greater than 12 hours.")
        return False

def data_frame_creator(file_name, dst_min, start_timestamp, end_timestamp, dawn_dusk = False, percentiles = False, ):
    #Function that makes the df that can be plotted

    # specify the dst minmum timestamp
    dst_min = pd.Timestamp(dst_min)    
    
    QDLat_cond      = 50  #Degrees

    # Reads in the data
    df = read_feather(dir+file_name)
    # Adds the orbits
    df_orbits =  new_orbit_cutter(df)

    df_cond_day     = conditions(df_orbits, start_timestamp=start_timestamp, 
                                end_timestamp=end_timestamp, QDLat_cond=QDLat_cond, 
                                dayside=('Dawn' if dawn_dusk else True))

    df_cond_night   = conditions(df_orbits, start_timestamp=start_timestamp, 
                                end_timestamp=end_timestamp, QDLat_cond=QDLat_cond, 
                                dayside=('Dusk' if dawn_dusk else False))

    # Resample dataframes 
    # df_resampled_day        = df_cond_day.groupby('Orbit_number')[['M_i_eff','Timestamp','M_i_eff_tbt_model' ,'MLT']].quantile(numeric_only=False)
    df_resampled_day = df_cond_day.groupby('Orbit_number')[['M_i_eff', 'Timestamp', 'M_i_eff_tbt_model', 'MLT']].agg({
    'M_i_eff': 'quantile', 
    'Timestamp': 'quantile',
    'M_i_eff_tbt_model': 'quantile',
    'MLT': 'quantile'})

    df_resampled_night      = df_cond_night.groupby('Orbit_number')[['M_i_eff', 'Timestamp', 'M_i_eff_tbt_model', 'MLT']].agg({
    'M_i_eff': 'quantile',  
    'Timestamp': 'quantile',
    'M_i_eff_tbt_model': 'quantile',
    'MLT': 'quantile'})

    if percentiles:
        df_resampled_day_25     = df_cond_day.groupby('Orbit_number')[['M_i_eff', 'Timestamp', 'M_i_eff_tbt_model', 'MLT']].agg({
        'M_i_eff': lambda x: x.quantile(0.25),  # calculate the 25th percentile of the 'M_i_eff' column
        'Timestamp': 'quantile',
        'M_i_eff_tbt_model': 'quantile',
        'MLT': 'quantile'})
        df_resampled_day_75     = df_cond_day.groupby('Orbit_number')[['M_i_eff', 'Timestamp', 'M_i_eff_tbt_model', 'MLT']].agg({
        'M_i_eff': lambda x: x.quantile(0.75),  # calculate the 75th percentile of the 'M_i_eff' column
        'Timestamp': 'quantile',
        'M_i_eff_tbt_model': 'quantile',
        'MLT': 'quantile'})
    
        df_resampled_night_25   = df_cond_night.groupby('Orbit_number')[['M_i_eff', 'Timestamp', 'M_i_eff_tbt_model', 'MLT']].agg({
        'M_i_eff': lambda x: x.quantile(0.25),  # calculate the 25th percentile of the 'M_i_eff' column
        'Timestamp': 'quantile',
        'M_i_eff_tbt_model': 'quantile',
        'MLT': 'quantile'})
        df_resampled_night_75   = df_cond_night.groupby('Orbit_number')[['M_i_eff', 'Timestamp', 'M_i_eff_tbt_model', 'MLT']].agg({
        'M_i_eff': lambda x: x.quantile(0.75),  # calculate the 75th percentile of the 'M_i_eff' column
        'Timestamp': 'quantile',
        'M_i_eff_tbt_model': 'quantile',
        'MLT': 'quantile'})
        
        return df_resampled_day, df_resampled_night, df_cond_day, df_cond_night, df_orbits,\
            df_resampled_day_25, df_resampled_day_75, df_resampled_night_25, df_resampled_night_75,
    else:
        return df_resampled_day, df_resampled_night, df_cond_day, df_cond_night, df_orbits

       
def plot_old(file_names, dst_min, dawn_dusk = False):
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
    df_A_night_resampled      = df_A_2_night.groupby('Orbit_number')[['M_i_eff','Timestamp','M_i_eff_tbt_model' ]].median(numeric_only=False)
    df_B__night_resampled      = df_B_2_night.groupby('Orbit_number')[['M_i_eff','Timestamp','M_i_eff_tbt_model' ]].median(numeric_only=False)
    df_C__night_resampled      = df_C_2_night.groupby('Orbit_number')[['M_i_eff','Timestamp','M_i_eff_tbt_model' ]].median(numeric_only=False)
    

def plot(file_names, dst_min, ax_num, dawn_dusk = False, delta_time = 3,):
    
    # specify the dst minmum timestamp
    dst_min = pd.Timestamp(dst_min)
    # Select the rows within +/- three days of the Dst minimum timestamp 
    start_timestamp = dst_min - pd.Timedelta(days=delta_time)
    end_timestamp   = dst_min + pd.Timedelta(days=delta_time)

    df_A_resampled, df_A__night_resampled, df_A_cond_day, df_A_cond_night, not_used \
        = data_frame_creator(file_names[0], 
                            dst_min, start_timestamp, end_timestamp,
                            dawn_dusk=(True if dawn_dusk else False),)
    
    df_B_resampled, df_B__night_resampled, df_B_cond_day, df_B_cond_night, not_used \
        = data_frame_creator(file_names[1], 
                            dst_min, start_timestamp, end_timestamp,
                            dawn_dusk = False,)

    df_C_resampled, df_C__night_resampled, df_C_cond_day, df_C_cond_night, not_used \
        = data_frame_creator(file_names[2], 
                            dst_min, start_timestamp, end_timestamp,
                            dawn_dusk=(True if dawn_dusk else False),)
    
    # Plotting
    ax[(0,0)].plot(df_A_resampled['Timestamp'],df_A_resampled['M_i_eff'], color = 'tab:blue',  label = f'Swarm A')
    ax[(1,0)].plot(df_B_resampled['Timestamp'],df_B_resampled['M_i_eff'], color = 'tab:red',   label = f'Swarm B')
    ax[(2,0)].plot(df_C_resampled['Timestamp'],df_C_resampled['M_i_eff'], color = 'tab:green', label = f'Swarm C')

    ax[(0,1)].plot(df_A__night_resampled['Timestamp'],df_A__night_resampled['M_i_eff'], color = 'tab:blue',  label = f'Swarm A')
    ax[(1,1)].plot(df_B__night_resampled['Timestamp'],df_B__night_resampled['M_i_eff'], color = 'tab:red',   label = f'Swarm B')
    ax[(2,1)].plot(df_C__night_resampled['Timestamp'],df_C__night_resampled['M_i_eff'], color = 'tab:green', label = f'Swarm C')

    #Plotting IRI 2016
    ax[(0,0)].plot(df_A_cond_day['Timestamp'],df_A_cond_day['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')
    ax[(1,0)].plot(df_B_cond_day['Timestamp'],df_B_cond_day['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')
    ax[(2,0)].plot(df_C_cond_day['Timestamp'],df_C_cond_day['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')
    ax[(0,1)].plot(df_A_cond_night['Timestamp'],df_A_cond_night['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')
    ax[(1,1)].plot(df_B_cond_night['Timestamp'],df_B_cond_night['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')
    ax[(2,1)].plot(df_C_cond_night['Timestamp'],df_C_cond_night['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')

    # #Plotting IRI 2016 all values
    # ax[(0,0)].plot(df_A_2['Timestamp'],df_A_2['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')
    # ax[(1,0)].plot(df_B_2['Timestamp'],df_B_2['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')
    # ax[(2,0)].plot(df_C_2['Timestamp'],df_C_2['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')
    # ax[(0,1)].plot(df_A_2_night['Timestamp'],df_A_2_night['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')
    # ax[(1,1)].plot(df_B_2_night['Timestamp'],df_B_2_night['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')
    # ax[(2,1)].plot(df_C_2_night['Timestamp'],df_C_2_night['M_i_eff_tbt_model'], color = 'black', ls = '--', label = f'IRI 2016')



    storm_name = ['June 2015', 'December 2015', 'September 2017', 'August 2018']
    

    for j in range(2):
        for i in range(3):
            ax[(i,j)].set_ylabel(r'Effective Ion Mass [u]')
            ax[(i,j)].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
            ax[(i,j)].legend(loc = 'best',  frameon=False,)
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
    
    # fig.legend(('Swarm A','Swarm B','Swarm C'),loc='center', bbox_to_anchor=(0.78, 0.52), ncol=3)

    # plt.xlabel('Orbit number')
    plt.suptitle(f'Median Effective Ion Mass per Orbit at {storm_name[ax_num]} Storm ')
    # plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(f'storm_data/Plots/TEST_Median Ion Mass per orbit at {storm_name[ax_num]} storm.png')
    # plt.show()

def plot_same_plot(file_names, dst_min, ax_num, dawn_dusk = False, delta_time = 3,):
    
    # specify the dst minmum timestamp
    dst_min = pd.Timestamp(dst_min)
    # Select the rows within +/- three days of the Dst minimum timestamp 
    start_timestamp = dst_min - pd.Timedelta(days=delta_time)
    end_timestamp   = dst_min + pd.Timedelta(days=delta_time)

    df_A_resampled, df_A_night_resampled, df_A_cond_day, df_A_cond_night, not_used, \
        df_A_resampled_day_25, df_A_resampled_day_75, df_A_resampled_night_25, df_A_resampled_night_75,\
        = data_frame_creator(file_names[0], 
                            dst_min, start_timestamp, end_timestamp,
                            dawn_dusk=(True if dawn_dusk else False),percentiles=True)
    
    df_B_resampled, df_B_night_resampled, df_B_cond_day, df_B_cond_night, not_used, \
        df_B_resampled_day_25, df_B_resampled_day_75, df_B_resampled_night_25, df_B_resampled_night_75,\
        = data_frame_creator(file_names[1], 
                            dst_min, start_timestamp, end_timestamp,
                            dawn_dusk = False,percentiles=True)

    df_C_resampled, df_C_night_resampled, df_C_cond_day, df_C_cond_night, not_used, \
        df_C_resampled_day_25, df_C_resampled_day_75, df_C_resampled_night_25, df_C_resampled_night_75,\
        = data_frame_creator(file_names[2], 
                            dst_min, start_timestamp, end_timestamp,
                            dawn_dusk=(True if dawn_dusk else False),percentiles=True)
    
    mlt_A_day, mlt_B_day, mlt_C_day =   df_A_resampled['MLT'].mean(), \
                                        df_B_resampled['MLT'].mean(), \
                                        df_C_resampled['MLT'].mean()
    mlt_A_ngt, mlt_B_ngt, mlt_C_ngt =   df_A_night_resampled['MLT'].mean(), \
                                        df_B_night_resampled['MLT'].mean(), \
                                        df_C_night_resampled['MLT'].mean()
    

    
    gap_A = check_time_gap(df_A_resampled)
    gap_B = check_time_gap(df_B_resampled)
    gap_C = check_time_gap(df_C_resampled)
    
    # Plotting effective ion mass
    if gap_A:
        df_A_resampled_part1 = df_A_resampled[df_A_resampled['Timestamp'] <= dst_min]
        df_A_resampled_part2 = df_A_resampled[df_A_resampled['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)+ pd.Timedelta(hours=7)]
        df_A_night_resampled_part1 = df_A_night_resampled[df_A_night_resampled['Timestamp'] <= dst_min]
        df_A_night_resampled_part2 = df_A_night_resampled[df_A_night_resampled['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        ax[0].plot(df_A_resampled_part1['Timestamp'],df_A_resampled_part1['M_i_eff'], marker = '*', color = 'tab:blue',  label = f'Swarm A MLT:{mlt_A_day:2.0f} {"(Dawnside)" if dawn_dusk else ""}')
        ax[0].plot(df_A_resampled_part2['Timestamp'],df_A_resampled_part2['M_i_eff'], marker = '*', color = 'tab:blue', )
        ax[1].plot(df_A_night_resampled_part1['Timestamp'],df_A_night_resampled_part1['M_i_eff'], marker = '*', color = 'tab:blue',  label = f'Swarm A MLT:{mlt_A_ngt:2.0f} {"(Duskside)" if dawn_dusk else ""}')
        ax[1].plot(df_A_night_resampled_part2['Timestamp'],df_A_night_resampled_part2['M_i_eff'], marker = '*', color = 'tab:blue', )
        
        df_A_resampled_day_25_part1 = df_A_resampled_day_25[df_A_resampled_day_25['Timestamp'] <= dst_min]
        df_A_resampled_day_25_part2 = df_A_resampled_day_25[df_A_resampled_day_25['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        df_A_resampled_day_75_part1 = df_A_resampled_day_75[df_A_resampled_day_75['Timestamp'] <= dst_min]
        df_A_resampled_day_75_part2 = df_A_resampled_day_75[df_A_resampled_day_75['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        ax[0].plot(df_A_resampled_day_25_part1['Timestamp'],df_A_resampled_day_25_part1['M_i_eff'], color = 'tab:blue',  ls='--',linewidth =0.5,)
        ax[0].plot(df_A_resampled_day_25_part2['Timestamp'],df_A_resampled_day_25_part2['M_i_eff'], color = 'tab:blue',  ls='--',linewidth =0.5,)
        ax[0].plot(df_A_resampled_day_75_part1['Timestamp'],df_A_resampled_day_75_part1['M_i_eff'], color = 'tab:blue',  ls='--',linewidth =0.5,)
        ax[0].plot(df_A_resampled_day_75_part2['Timestamp'],df_A_resampled_day_75_part2['M_i_eff'], color = 'tab:blue',  ls='--',linewidth =0.5,)

        df_A_resampled_night_25_part1 = df_A_resampled_night_25[df_A_resampled_night_25['Timestamp'] <= dst_min]
        df_A_resampled_night_25_part2 = df_A_resampled_night_25[df_A_resampled_night_25['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        df_A_resampled_night_75_part1 = df_A_resampled_night_75[df_A_resampled_night_75['Timestamp'] <= dst_min]
        df_A_resampled_night_75_part2 = df_A_resampled_night_75[df_A_resampled_night_75['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        ax[1].plot(df_A_resampled_night_25_part1['Timestamp'],df_A_resampled_night_25_part1['M_i_eff'], color = 'tab:blue',  ls='--',linewidth =0.5,)
        ax[1].plot(df_A_resampled_night_25_part2['Timestamp'],df_A_resampled_night_25_part2['M_i_eff'], color = 'tab:blue',  ls='--',linewidth =0.5,)
        ax[1].plot(df_A_resampled_night_75_part1['Timestamp'],df_A_resampled_night_75_part1['M_i_eff'], color = 'tab:blue',  ls='--',linewidth =0.5,)
        ax[1].plot(df_A_resampled_night_75_part2['Timestamp'],df_A_resampled_night_75_part2['M_i_eff'], color = 'tab:blue',  ls='--',linewidth =0.5,)

    else:
        ax[0].plot(df_A_resampled['Timestamp'],df_A_resampled['M_i_eff'], marker = '*', color = 'tab:blue',  label = f'Swarm A MLT:{mlt_A_day:2.0f} {"(Dawnside)" if dawn_dusk else ""}')
        ax[1].plot(df_A_night_resampled['Timestamp'],df_A_night_resampled['M_i_eff'], marker = '*', color = 'tab:blue',  label = f'Swarm A MLT:{mlt_A_ngt:2.0f} {"(Duskside)" if dawn_dusk else ""}')
        ax[0].plot(df_A_resampled_day_25['Timestamp'],df_A_resampled_day_25['M_i_eff'], color = 'tab:blue',  ls='--',linewidth =0.5,)
        ax[0].plot(df_A_resampled_day_75['Timestamp'],df_A_resampled_day_75['M_i_eff'], color = 'tab:blue',  ls='--',linewidth =0.5,)
        ax[1].plot(df_A_resampled_night_25['Timestamp'],df_A_resampled_night_25['M_i_eff'], color = 'tab:blue',  ls='--',linewidth =0.5,)
        ax[1].plot(df_A_resampled_night_75['Timestamp'],df_A_resampled_night_75['M_i_eff'], color = 'tab:blue',  ls='--',linewidth =0.5,)
    

    if gap_B:
        df_B_resampled_part1 = df_B_resampled[df_B_resampled['Timestamp'] <= dst_min]
        df_B_resampled_part2 = df_B_resampled[df_B_resampled['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        df_B_night_resampled_part1 = df_B_night_resampled[df_B_night_resampled['Timestamp'] <= dst_min]
        df_B_night_resampled_part2 = df_B_night_resampled[df_B_night_resampled['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        ax[0].plot(df_B_resampled_part1['Timestamp'],df_B_resampled_part1['M_i_eff'], marker = '*', color = 'tab:red',  label = f'Swarm B MLT:{mlt_B_day:2.0f}')
        ax[0].plot(df_B_resampled_part2['Timestamp'],df_B_resampled_part2['M_i_eff'], marker = '*', color = 'tab:red', )
        ax[1].plot(df_B_night_resampled_part1['Timestamp'],df_B_night_resampled_part1['M_i_eff'], marker = '*', color = 'tab:red',  label = f'Swarm B MLT:{mlt_B_ngt:2.0f}')
        ax[1].plot(df_B_night_resampled_part2['Timestamp'],df_B_night_resampled_part2['M_i_eff'], marker = '*', color = 'tab:red',)

        df_B_resampled_day_25_part1 = df_B_resampled_day_25[df_B_resampled_day_25['Timestamp'] <= dst_min]
        df_B_resampled_day_25_part2 = df_B_resampled_day_25[df_B_resampled_day_25['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        df_B_resampled_day_75_part1 = df_B_resampled_day_75[df_B_resampled_day_75['Timestamp'] <= dst_min]
        df_B_resampled_day_75_part2 = df_B_resampled_day_75[df_B_resampled_day_75['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        ax[0].plot(df_B_resampled_day_25_part1['Timestamp'],df_B_resampled_day_25_part1['M_i_eff'], color = 'tab:red',  ls='--',linewidth =0.5,)
        ax[0].plot(df_B_resampled_day_25_part2['Timestamp'],df_B_resampled_day_25_part2['M_i_eff'], color = 'tab:red',  ls='--',linewidth =0.5,)
        ax[0].plot(df_B_resampled_day_75_part1['Timestamp'],df_B_resampled_day_75_part1['M_i_eff'], color = 'tab:red',  ls='--',linewidth =0.5,)
        ax[0].plot(df_B_resampled_day_75_part2['Timestamp'],df_B_resampled_day_75_part2['M_i_eff'], color = 'tab:red',  ls='--',linewidth =0.5,)

        df_B_resampled_night_25_part1 = df_B_resampled_night_25[df_B_resampled_night_25['Timestamp'] <= dst_min]
        df_B_resampled_night_25_part2 = df_B_resampled_night_25[df_B_resampled_night_25['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        df_B_resampled_night_75_part1 = df_B_resampled_night_75[df_B_resampled_night_75['Timestamp'] <= dst_min]
        df_B_resampled_night_75_part2 = df_B_resampled_night_75[df_B_resampled_night_75['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        ax[1].plot(df_B_resampled_night_25_part1['Timestamp'],df_B_resampled_night_25_part1['M_i_eff'], color = 'tab:red',  ls='--',linewidth =0.5,)
        ax[1].plot(df_B_resampled_night_25_part2['Timestamp'],df_B_resampled_night_25_part2['M_i_eff'], color = 'tab:red',  ls='--',linewidth =0.5,)
        ax[1].plot(df_B_resampled_night_75_part1['Timestamp'],df_B_resampled_night_75_part1['M_i_eff'], color = 'tab:red',  ls='--',linewidth =0.5,)
        ax[1].plot(df_B_resampled_night_75_part2['Timestamp'],df_B_resampled_night_75_part2['M_i_eff'], color = 'tab:red',  ls='--',linewidth =0.5,)


    else:
        ax[0].plot(df_B_resampled['Timestamp'],df_B_resampled['M_i_eff'], marker = '*', color = 'tab:red',   label = f'Swarm B MLT:{mlt_B_day:2.0f} ')
        ax[1].plot(df_B_night_resampled['Timestamp'],df_B_night_resampled['M_i_eff'], marker = '*', color = 'tab:red',   label = f'Swarm B MLT:{mlt_B_ngt:2.0f} ')
        ax[0].plot(df_B_resampled_day_25['Timestamp'],df_B_resampled_day_25['M_i_eff'], color = 'tab:red',  ls='--',linewidth =0.5,)
        ax[0].plot(df_B_resampled_day_75['Timestamp'],df_B_resampled_day_75['M_i_eff'], color = 'tab:red',  ls='--',linewidth =0.5,)
        ax[1].plot(df_B_resampled_night_25['Timestamp'],df_B_resampled_night_25['M_i_eff'], color = 'tab:red',  ls='--',linewidth =0.5,)
        ax[1].plot(df_B_resampled_night_75['Timestamp'],df_B_resampled_night_75['M_i_eff'], color = 'tab:red',  ls='--',linewidth =0.5,)
    
    if gap_C:
        df_C_resampled_part1 = df_C_resampled[df_C_resampled['Timestamp'] <= dst_min]
        df_C_resampled_part2 = df_C_resampled[df_C_resampled['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        df_C_night_resampled_part1 = df_C_night_resampled[df_C_night_resampled['Timestamp'] <= dst_min]
        df_C_night_resampled_part2 = df_C_night_resampled[df_C_night_resampled['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        ax[0].plot(df_C_resampled_part1['Timestamp'],df_C_resampled_part1['M_i_eff'], marker = '*', color = 'tab:green',  label = f'Swarm C MLT:{mlt_C_day:2.0f} {"(Dawnside)" if dawn_dusk else ""}')
        ax[0].plot(df_C_resampled_part2['Timestamp'],df_C_resampled_part2['M_i_eff'], marker = '*', color = 'tab:green', )
        ax[1].plot(df_C_night_resampled_part1['Timestamp'],df_C_night_resampled_part1['M_i_eff'], marker = '*', color = 'tab:green',  label = f'Swarm C MLT:{mlt_C_ngt:2.0f} {"(Duskside)" if dawn_dusk else ""}')
        ax[1].plot(df_C_night_resampled_part2['Timestamp'],df_C_night_resampled_part2['M_i_eff'], marker = '*', color = 'tab:green',)

        df_C_resampled_day_25_part1 = df_C_resampled_day_25[df_C_resampled_day_25['Timestamp'] <= dst_min]
        df_C_resampled_day_25_part2 = df_C_resampled_day_25[df_C_resampled_day_25['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        df_C_resampled_day_75_part1 = df_C_resampled_day_75[df_C_resampled_day_75['Timestamp'] <= dst_min]
        df_C_resampled_day_75_part2 = df_C_resampled_day_75[df_C_resampled_day_75['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        ax[0].plot(df_C_resampled_day_25_part1['Timestamp'],df_C_resampled_day_25_part1['M_i_eff'], color = 'tab:green',  ls='--',linewidth =0.5,)
        ax[0].plot(df_C_resampled_day_25_part2['Timestamp'],df_C_resampled_day_25_part2['M_i_eff'], color = 'tab:green',  ls='--',linewidth =0.5,)
        ax[0].plot(df_C_resampled_day_75_part1['Timestamp'],df_C_resampled_day_75_part1['M_i_eff'], color = 'tab:green',  ls='--',linewidth =0.5,)
        ax[0].plot(df_C_resampled_day_75_part2['Timestamp'],df_C_resampled_day_75_part2['M_i_eff'], color = 'tab:green',  ls='--',linewidth =0.5,)

        df_C_resampled_night_25_part1 = df_C_resampled_night_25[df_C_resampled_night_25['Timestamp'] <= dst_min]
        df_C_resampled_night_25_part2 = df_C_resampled_night_25[df_C_resampled_night_25['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        df_C_resampled_night_75_part1 = df_C_resampled_night_75[df_C_resampled_night_75['Timestamp'] <= dst_min]
        df_C_resampled_night_75_part2 = df_C_resampled_night_75[df_C_resampled_night_75['Timestamp'] >= dst_min+ pd.Timedelta(hours=7)]
        ax[1].plot(df_C_resampled_night_25_part1['Timestamp'],df_C_resampled_night_25_part1['M_i_eff'], color = 'tab:green',  ls='--',linewidth =0.5,)
        ax[1].plot(df_C_resampled_night_25_part2['Timestamp'],df_C_resampled_night_25_part2['M_i_eff'], color = 'tab:green',  ls='--',linewidth =0.5,)
        ax[1].plot(df_C_resampled_night_75_part1['Timestamp'],df_C_resampled_night_75_part1['M_i_eff'], color = 'tab:green',  ls='--',linewidth =0.5,)
        ax[1].plot(df_C_resampled_night_75_part2['Timestamp'],df_C_resampled_night_75_part2['M_i_eff'], color = 'tab:green',  ls='--',linewidth =0.5,)

    else:
        ax[0].plot(df_C_resampled['Timestamp'],df_C_resampled['M_i_eff'], marker = '*', color = 'tab:green', label = f'Swarm C MLT:{mlt_C_day:2.0f} {"(Dawnside)" if dawn_dusk else ""}')
        ax[1].plot(df_C_night_resampled['Timestamp'],df_C_night_resampled['M_i_eff'], marker = '*', color = 'tab:green', label = f'Swarm C MLT:{mlt_C_ngt:2.0f} {"(Duskside)" if dawn_dusk else ""}')
        ax[0].plot(df_C_resampled_day_25['Timestamp'],df_C_resampled_day_25['M_i_eff'], color = 'tab:green',  ls='--',linewidth =0.5,)
        ax[0].plot(df_C_resampled_day_75['Timestamp'],df_C_resampled_day_75['M_i_eff'], color = 'tab:green',  ls='--',linewidth =0.5,)
        ax[1].plot(df_C_resampled_night_25['Timestamp'],df_C_resampled_night_25['M_i_eff'], color = 'tab:green',  ls='--',linewidth =0.5,)
        ax[1].plot(df_C_resampled_night_75['Timestamp'],df_C_resampled_night_75['M_i_eff'], color = 'tab:green',  ls='--',linewidth =0.5,)

    # #Plotting IRI 2016 all values
    # ax[0].plot(df_A_resampled['Timestamp'],df_A_resampled['M_i_eff_tbt_model'], color = 'tab:blue', ls = '--', linewidth =1.5)
    # ax[0].plot(df_B_resampled['Timestamp'],df_B_resampled['M_i_eff_tbt_model'], color = 'tab:red', ls = '--', linewidth =1.5)
    # ax[0].plot(df_C_resampled['Timestamp'],df_C_resampled['M_i_eff_tbt_model'], color = 'tab:green', ls = '--', linewidth =1.5)
    # ax[1].plot(df_A_night_resampled['Timestamp'],df_A_night_resampled['M_i_eff_tbt_model'], color = 'tab:blue', ls = '--', linewidth =1.5)
    # ax[1].plot(df_B_night_resampled['Timestamp'],df_B_night_resampled['M_i_eff_tbt_model'], color = 'tab:red', ls = '--', linewidth =1.5)
    # ax[1].plot(df_C_night_resampled['Timestamp'],df_C_night_resampled['M_i_eff_tbt_model'], color = 'tab:green', ls = '--', linewidth =1.5)


    storm_name = ['June 2015', 'December 2015', 'September 2017', 'August 2018']
    

    for j in range(2):
        
        ax[j].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
        ax[j].yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
        ax[j].legend(loc = 'best', framealpha=1, ).set_zorder(10)
        ax[j].axhline(y = 16, color = 'black', ls = '--',linewidth=1)
        ax[j].axvline(x = dst_min, color = 'black', ls = '--',linewidth=1)
        ax[j].set_xlim(start_timestamp, end_timestamp)
        ax[j].set_ylim(0, 20)
        ax[j].locator_params(axis="y", integer=True, tight=True)
        ax[j].set_facecolor('#EBEBEB')
        ax[j].grid(which='major', color='white', linewidth=1.2)
        ax[j].grid(which='minor', color='white', linewidth=0.6)
        ax[j].xaxis.set_major_formatter(mdates.DateFormatter('%d'))
        ax[j].set_xlabel('Day of month')
    ax[0].set_ylabel(r'Effective Ion Mass [u]')
    ax[0].set_title(f'Dayside')
    ax[1].set_title(f'Nightside')

        #Dst-plotter
    dir_dst = 'storm_data/omni_data/'
    file_names_dst = ['2015_June.txt','2015_December.txt','2017_September.txt','2018_August.txt']
    from read_txt_omni import readfile
    df,df2 = readfile(dir_dst+file_names_dst[ax_num])
    ax3 = ax[1].twinx()
    ax3.plot(df2.index, df2['SYM/H_INDEX']*-1, ls='solid',color='black',zorder=1)
    ax3.set_yticklabels([])  
    ax3.set_ylim(-100,400)  
    ax3.axhline(y = 0, color = 'black', ls = '--',linewidth=1)

    
    plt.suptitle(f'Orbital Median of Effective Ion Mass during {storm_name[ax_num]} Storm ')
    # plt.gcf().autofmt_xdate()
    plt.savefig(f'storm_data/Plots/TEST_Median Ion Mass per orbit at {storm_name[ax_num]} storm.png')
    # plt.show()


def plot_baseline(file_name, mid_time, ):
    
    # specify the middle timestamp
    mid_time = pd.Timestamp(mid_time)
    
    # Select the rows within +/- three days of the middle timestamp
    delta_time = 3
    start_timestamp = mid_time - pd.Timedelta(days=delta_time)
    end_timestamp   = mid_time + pd.Timedelta(days=delta_time)

    df_resampled, df_night_resampled, df_cond_day, df_cond_night, df_orbits, \
     df_resampled_day_25, df_resampled_day_75, df_resampled_night_25, df_resampled_night_75,\
        = data_frame_creator(file_name, mid_time, start_timestamp, end_timestamp,percentiles=True)
    

    num_orbits = df_cond_day['Orbit_number'].nunique()
    test_orbit = int(num_orbits-20/2)
    
    single_orbit_day    = df_cond_day[df_cond_day['Orbit_number'] == test_orbit]
    single_orbit_night  = df_cond_night[df_cond_night['Orbit_number'] == test_orbit]
    # single_orbit_night_part1 = single_orbit_night[single_orbit_night['Timestamp'] <= single_orbit_day['Timestamp'][0]]
#     single_orbit_night_part2 = single_orbit_night[single_orbit_night['Timestamp'] >= single_orbit_day['Timestamp'][0]]
    

    mlt_day                 = df_resampled['MLT'].mean()
    mlt_night               = df_night_resampled['MLT'].mean()
    mlt_single_orbit        = single_orbit_day['MLT'].mean()
    mlt_single_orbit_ngt    = single_orbit_night['MLT'].mean()
    
    plt.figure(1, figsize=(6.9,4.8))
    plt.plot(df_resampled['Timestamp'],df_resampled['M_i_eff'], color = 'tab:blue',  label = f'Dayside   (MLT:{mlt_day:.0f})')
    plt.plot(df_night_resampled['Timestamp'],df_night_resampled['M_i_eff'], color = 'tab:red',  label = f'Nightside (MLT:{mlt_night:.0f})')
    plt.plot(df_resampled_day_25['Timestamp'],df_resampled_day_25['M_i_eff'], color = 'tab:blue',  ls='--',linewidth =0.5,label='25th/75th percentile')
    plt.plot(df_resampled_day_75['Timestamp'],df_resampled_day_75['M_i_eff'], color = 'tab:blue',  ls='--',linewidth =0.5,)
    plt.plot(df_resampled_night_25['Timestamp'],df_resampled_night_25['M_i_eff'], color = 'tab:red',  ls='--',linewidth =0.5,label='25th/75th percentile')
    plt.plot(df_resampled_night_75['Timestamp'],df_resampled_night_75['M_i_eff'], color = 'tab:red',  ls='--',linewidth =0.5,)
    plt.scatter(df_resampled['Timestamp'][test_orbit],df_resampled['M_i_eff'][test_orbit], color = 'blue',  zorder=2)#label = r'Median (Orbit #'+f'{test_orbit})')
    plt.scatter(df_night_resampled['Timestamp'][test_orbit],df_night_resampled['M_i_eff'][test_orbit], color = 'm',  zorder=2)#label = r'Median (Orbit #' +f'{test_orbit})')
    plt.plot(df_resampled['Timestamp'],df_resampled['M_i_eff_tbt_model'], color = 'tab:cyan',  label = f'IRI 2016', ls='--')   
    plt.plot(df_night_resampled['Timestamp'],df_night_resampled['M_i_eff_tbt_model'], color = 'tab:orange',  label = f'IRI 2016', ls='--')   

    plt.fill_between(df_resampled['Timestamp'], df_resampled_day_25['M_i_eff'], df_resampled_day_75['M_i_eff'], color='blue', alpha=0.1)
    plt.fill_between(df_resampled_night_75['Timestamp'], df_resampled_night_25['M_i_eff'], df_resampled_night_75['M_i_eff'], color='red', alpha=0.1)

    plt.ylabel(r'Effective Ion Mass [u]')
    plt.xlabel(r'Time [UT]')
    plt.legend(loc = 'best',framealpha=0.3,ncol=3, )
    plt.axhline(y = 16, color = 'black', ls = '--',linewidth=1)
    plt.gca().locator_params(axis="y", integer=True, tight=True)
    plt.gca().set_facecolor('#EBEBEB')
    plt.gca().grid(which='major', color='white', linewidth=1.2)
    plt.gca().grid(which='minor', color='white', linewidth=0.6)
    plt.gca().xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
    plt.gca().yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    plt.xlim(start_timestamp, end_timestamp)
    plt.title(r'Plot of orbital median of $M_{eff}$ a quiet week')
    plt.ylim(0,20)
    plt.gcf().autofmt_xdate()
    plt.savefig(f'storm_data/Plots/Quiet week - Orbital median.png')

    
    plt.figure(2)
    plt.plot(single_orbit_day['Timestamp'],single_orbit_day['M_i_eff'], color = 'tab:blue',  label = f'Dayside   (MLT:{mlt_single_orbit:.0f})', zorder=2)
    plt.plot(single_orbit_night['Timestamp'],single_orbit_night['M_i_eff'], color = 'tab:red',  label = f'Nightside (MLT:{mlt_single_orbit_ngt:.0f})', zorder=2)
    # plt.plot(single_orbit_night_part2['Timestamp'],single_orbit_night_part2['M_i_eff'], color = 'tab:red', )
    plt.scatter(df_resampled['Timestamp'][test_orbit],df_resampled['M_i_eff'][test_orbit], color = 'blue',  label = r'Orbital median value dayside', zorder=3)
    plt.scatter(df_night_resampled['Timestamp'][test_orbit],df_night_resampled['M_i_eff'][test_orbit], color = 'm',  label = r'Orbital median value nightside', zorder=3)
    plt.ylabel(r'Effective Ion Mass [u]')
    plt.xlabel(r'Time [UT]')
    plt.legend(loc = 'lower left')
    plt.axhline(y = 16, color = 'black', ls = '--',linewidth=1)
    plt.gca().locator_params(axis="y", integer=True, tight=True)
    plt.gca().set_facecolor('#EBEBEB')
    plt.gca().grid(which='major', color='white', linewidth=1.2)
    plt.gca().grid(which='minor', color='white', linewidth=0.6)
    plt.gca().xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
    plt.gca().yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    plt.title(f'Plot of one orbit by Swarm A a quiet day '+f'({df_resampled["Timestamp"].dt.date[test_orbit]})')
    plt.ylim(0,20)
    # plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    plt.savefig(f'storm_data/Plots/Quiet orbit - Full orbit a quiet day.png')



def full_orbit_plotter(name,storm=False):
    
    # Reads in the data
    dfA = read_feather(dir+name)
    # Adds the orbits
    df_orbits =  new_orbit_cutter(dfA)

    # Resample dataframes 
    # df_resampled    = dfA.groupby('Orbit_number')[['M_i_eff','Timestamp','M_i_eff_tbt_model' ,'MLT']].median(numeric_only=False)
    # df_resampled_night  = dfA.groupby('Orbit_number')[['M_i_eff','Timestamp','M_i_eff_tbt_model' ,'MLT']].median(numeric_only=False)

    mid_time   = '2016-11-17 00:00:00'
    

    num_orbits = df_orbits['Orbit_number'].nunique()
    print(num_orbits)
    test_orbit = int((num_orbits +12)/2) 
    print(test_orbit)
    single_full_orbit   = df_orbits[df_orbits['Orbit_number'] == test_orbit]


    cond_day = (single_full_orbit['MLT'] >= 8) & (single_full_orbit['MLT'] <= 16)
    cond_ngt = (single_full_orbit['MLT'] >= 20) | (single_full_orbit['MLT'] <= 4)
    cond_lat    = (single_full_orbit['QDLatitude'] >= -50)   & (single_full_orbit['QDLatitude'] <= 50)
    dayside_orbit   = single_full_orbit[cond_day & cond_lat]
    ngtside_orbit   = single_full_orbit[cond_ngt & cond_lat]

    mlt_day = dayside_orbit['MLT'].median()
    mlt_ngt = ngtside_orbit['MLT'].median()

    plt.figure(3)
    plt.plot(single_full_orbit['Timestamp'],single_full_orbit['M_i_eff'], color = 'black',  )
    plt.plot(dayside_orbit['Timestamp'],dayside_orbit['M_i_eff'], color = 'tab:red',  label = f'Dayside    MLT:{mlt_day:2.0f}')
    plt.plot(ngtside_orbit['Timestamp'],ngtside_orbit['M_i_eff'], color = 'tab:blue',  label = f'Nightside  MLT:{mlt_ngt:2.0f}')
    plt.ylabel(r'Effective Ion Mass [u]')
    plt.xlabel(r'Time [UT]')
    plt.legend(loc = 'lower right')
    plt.axhline(y = 16, color = 'black', ls = '--',linewidth=1)
    plt.gca().locator_params(axis="y", integer=True, tight=True)
    plt.gca().set_facecolor('#EBEBEB')
    plt.gca().grid(which='major', color='white', linewidth=1.2)
    plt.gca().grid(which='minor', color='white', linewidth=0.6)
    plt.gca().xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
    plt.gca().yaxis.set_minor_locator(ticker.AutoMinorLocator(5))
    plt.ylim(0,20)
    # plt.gcf().autofmt_xdate()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    if not storm:
        plt.title(f'Plot of one full orbit by Swarm A a random day '+f'({single_full_orbit["Timestamp"].dt.date[test_orbit]})')
        plt.savefig(f'storm_data/Plots/Quiet orbit - Quiet full orbit' +f'({single_full_orbit["Timestamp"].dt.date[test_orbit]}).png')

    else:
        plt.title(f'Plot of one full orbit by Swarm C a storm day '+f'({single_full_orbit["Timestamp"].dt.date[test_orbit]})')
        plt.savefig(f'storm_data/Plots/Full orbit a storm day.png')



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

###OLD PART OF CODE; NOT IN USE#
    # for i, element in enumerate([june_dst_min, december_dst_min, september_dst_min, august_dst_min]):
    #     fig, ax = plt.subplots(3,2,figsize=(25,15))#sharex=True,) 
    #     # If statement to make sure dawn/dusk for December storm is included
    #     if i == 1:
    #         plot(file_names=name_list[i], dst_min=element, ax_num = i, dawn_dusk = True)        
    #     else:
    #         plot(file_names=name_list[i], dst_min=element, ax_num = i, )
    #     # plt.show()
    #     plt.close()
###

    for i, element in enumerate([june_dst_min, december_dst_min, september_dst_min, august_dst_min]):
        plt.rcParams.update({'font.size': 20})
        fig, ax = plt.subplots(1,2,figsize=(15,10))
        plt.subplots_adjust( wspace=0.1)
        # plt.tight_layout() 
        # If statement to make sure dawn/dusk for December storm is included
        if i == 1:
            plot_same_plot(file_names=name_list[i], dst_min=element, ax_num = i, dawn_dusk = True)        
        else:
            plot_same_plot(file_names=name_list[i], dst_min=element, ax_num = i, )
        # plt.subplot_tool()
        # plt.show()
        plt.close()
    

    # #Baseline file name
    plt.rcdefaults()
    baseline_jun_A = 'Baseline_before_2017_09_sat_A' # Know that works
    baseline_jun_A = 'Baseline_before_2015_06_sat_B'
    baseline_jun_A = 'Baseline_before_2018_08_sat_A'
    # Middle time in baseline data
    baseline_mid_time   = '2017-09-02 00:00:00' # Know that works
    baseline_mid_time   = '2015-06-17 00:00:00'
    baseline_mid_time   = '2018-08-19 00:00:00'

    plot_baseline(baseline_jun_A, baseline_mid_time)
    plt.close()

    # Full orbit plotter
    full_orbit_plotter('quiet_days_sat_A')
    plt.close()
    full_orbit_plotter('2015_06_sat_C', storm=True)
    plt.close()