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
    df.set_index('Timestamp', inplace=True)
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

    df.loc[df.index[sign_index_list], 'Orbit_number'] = 1
  
    # Define the first orbit as the datapoints before the first crossing of the equator
    df['Orbit_number'][:sign_index_list[0]] = 1
    # Loops through the indecies and adds an orbit number 
    for i, element in enumerate(sign_index_list[:-2]):
        df['Orbit_number'][element:sign_index_list[i+1]] = i+1
    # Define the last orbit as the datapoints after the last crossing of the equator 
    else: 
        df['Orbit_number'][sign_index_list[i+1]:] = i+2

    return df

def conditions(df, start_timestamp, end_timestamp, QDLat_cond = 15, dayside =None,):
    if dayside:
        cond_day = (df['MLT'] >= 8) & (df['MLT'] <= 16)
        cond_nominal = (df['M_i_eff_Flags'] == 0)
    elif not dayside:
        cond_day = (df['MLT'] >= 20) | (df['MLT'] <= 4)
        cond_nominal = (df['M_i_eff_Flags'] == 0)
        
    elif dayside == None:
        cond_day = (df['MLT'] >= 0)
    
    cond_time   = (df.index >= start_timestamp) & (df.index <= end_timestamp)
    cond_lat    = (df['QDLatitude'] >= -QDLat_cond)   & (df['QDLatitude'] <= QDLat_cond) 

    

    df2 = df.loc[(cond_day  & 
                 cond_time &
                 cond_lat &
                 cond_nominal)]
    
    return df2

        

def plot(file_names, dst_min, ax_num, column = 'M_i_eff'):
    #Function that plots +/- 3 days of Dst-minimum 

    delta_time      = 4  # days 
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

    # df_A_2 = df_A.loc[(df_A.index >= start_timestamp)       & (df_A.index <= end_timestamp) # Conditions for time 
    #                 & (df_A['QDLatitude'] >= -QDLat_cond)   & (df_A['QDLatitude'] <= QDLat_cond)    # Conditions for equatorial region
    #                 & (df_A['MLT'] >= 8)                  & (df_A['MLT'] <= 16)]          # Conditions for dayside 
    # df_B_2 = df_B.loc[(df_B.index >= start_timestamp)       & (df_B.index <= end_timestamp)
    #                 & (df_B['QDLatitude'] >= -QDLat_cond)   & (df_B['QDLatitude'] <= QDLat_cond)
    #                 & (df_B['MLT'] >= 8)                  & (df_B['MLT'] <= 16)]
    # df_C_2 = df_C.loc[(df_C.index >= start_timestamp)       & (df_C.index <= end_timestamp)
    #                 & (df_C['QDLatitude'] >= -QDLat_cond)   & (df_C['QDLatitude'] <= QDLat_cond)
    #                 & (df_C['MLT'] >= 8)                  & (df_C['MLT'] <= 16)]
    
    df_A_2          = conditions(df_A, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                        QDLat_cond=QDLat_cond, dayside=True)
    df_B_2          = conditions(df_B, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                        QDLat_cond=QDLat_cond, dayside=True)
    df_C_2          = conditions(df_C, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                        QDLat_cond=QDLat_cond, dayside=True)
    
    df_A_2_night    = conditions(df_A, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                        QDLat_cond=QDLat_cond, dayside=False)
    df_B_2_night    = conditions(df_B, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                        QDLat_cond=QDLat_cond, dayside=False)
    df_C_2_night    = conditions(df_C, start_timestamp=start_timestamp, end_timestamp=end_timestamp,
                        QDLat_cond=QDLat_cond, dayside=False)
    
    

    
    # df_A_resampled      = df_A_2[column].resample(f'{resample_freq}H').median()
    # df_B_resampled      = df_B_2[column].resample(f'{resample_freq}H').median()
    # df_C_resampled      = df_C_2[column].resample(f'{resample_freq}H').median()
    # df_A_resampled_n_i  = df_A_2['N_i'].resample(f'{resample_freq}H').median() 
    # df_B_resampled_n_i  = df_B_2['N_i'].resample(f'{resample_freq}H').median() 
    # df_C_resampled_n_i  = df_C_2['N_i'].resample(f'{resample_freq}H').median() 
    df_A_resampled      = df_A_2.groupby('Orbit_number',as_index=False)[column].agg('median')
    df_B_resampled      = df_B_2.groupby('Orbit_number',as_index=False)[column].agg('median')
    df_C_resampled      = df_C_2.groupby('Orbit_number',as_index=False)[column].agg('median')


    df_A_resampled_n_i  = df_A_2.groupby('Orbit_number',as_index=False)['N_i'].agg('median') 
    df_B_resampled_n_i  = df_B_2.groupby('Orbit_number',as_index=False)['N_i'].agg('median') 
    df_C_resampled_n_i  = df_C_2.groupby('Orbit_number',as_index=False)['N_i'].agg('median') 



    
    # # create a dictionary of the mapping from df2
    # mapping1 = dict(zip(df_A_resampled['Orbit_number'], df_A_resampled['M_i_eff']))
    # mapping2 = dict(zip(df_B_resampled['Orbit_number'], df_B_resampled['M_i_eff']))
    # mapping3 = dict(zip(df_C_resampled['Orbit_number'], df_C_resampled['M_i_eff']))

    # # use the map method of df1 to replace the values in Col2 based on the mapping
    # df_A_2['M_i_eff'] = df_A_2['Orbit_number'].map(mapping1).fillna(df_A_2['M_i_eff'])
    # df_B_2['M_i_eff'] = df_B_2['Orbit_number'].map(mapping2).fillna(df_B_2['M_i_eff'])
    # df_C_2['M_i_eff'] = df_C_2['Orbit_number'].map(mapping3).fillna(df_C_2['M_i_eff'])
    
    df_list = [df_A_2,     df_B_2,     df_C_2, df_A_2_night, df_B_2_night, df_C_2_night]

    # for element in df_list:
    #     for value in element['M_i_eff_Flags']:
    #         print(value)

    # convert the timestamp index to a float index ranging from -delta_time to +delta_time
    index_min, index_max = -delta_time, delta_time
    
    index_range = index_max - index_min
    for element in df_list:
        element.index = element.index.astype(np.int64) * 1e-9
        element.index = ((element.index - element.index.min()) / (element.index.max() 
                        - element.index.min())) * index_range + index_min    
    
    # fig.align_ylabels()

    # #Boxplot test
    # for df in df_list:
    #     df['Orbit_number'] = pd.Categorical(df['Orbit_number'])
    #     df.boxplot(column='M_i_eff',by='Orbit_number')


    ax[(0,0)].plot(df_A_2.index,df_A_2['M_i_eff'], color = 'tab:blue',  label = f'SWARM A')
    ax[(1,0)].plot(df_B_2.index,df_B_2['M_i_eff'], color = 'tab:red',   label = f'SWARM B')
    ax[(2,0)].plot(df_C_2.index,df_C_2['M_i_eff'], color = 'tab:green', label = f'SWARM C')

    ax[(0,1)].plot(df_A_2_night.index,df_A_2_night['M_i_eff'], color = 'tab:blue',  label = f'SWARM A')
    ax[(1,1)].plot(df_B_2_night.index,df_B_2_night['M_i_eff'], color = 'tab:red',   label = f'SWARM B')
    ax[(2,1)].plot(df_C_2_night.index,df_C_2_night['M_i_eff'], color = 'tab:green', label = f'SWARM C')
    # IRI model
    ax[(0,0)].plot(df_A_2.index,df_A_2['M_i_eff_tbt_model'], color = 'black',  ls='--',label = f'IRI')
    ax[(1,0)].plot(df_B_2.index,df_B_2['M_i_eff_tbt_model'], color = 'black',   ls='--',label = f'IRI')
    ax[(2,0)].plot(df_C_2.index,df_C_2['M_i_eff_tbt_model'], color = 'black', ls='--',label = f'IRI')
    ax[(0,1)].plot(df_A_2_night.index,df_A_2_night['M_i_eff_tbt_model'], color = 'black', ls= '--',  label = f'IRI')
    ax[(1,1)].plot(df_B_2_night.index,df_B_2_night['M_i_eff_tbt_model'], color = 'black', ls= '--',   label = f'IRI')
    ax[(2,1)].plot(df_C_2_night.index,df_C_2_night['M_i_eff_tbt_model'], color = 'black', ls= '--', label = f'IRI')

    # ax2 = ax[ax_num].twinx()
    # ax2.set_ylim(0,1e6)
    # ax2.set_ylabel(r'Ion density [cm$^3$]')
    # ax2.plot(df_A_resampled_n_i, color = 'tab:blue',  ls='--', label = f'SWARM A')
    # ax2.plot(df_B_resampled_n_i, color = 'tab:red',   ls='--', label = f'SWARM B')
    # ax2.plot(df_C_resampled_n_i, color = 'tab:green', ls='--', label = f'SWARM C')


    storm_name = ['June 2015', 'December 2015', 'September 2017', 'August 2018']
    # ax[ax_num].set_title(f'{storm_name[ax_num]}')
    # ax[ax_num].set_ylim(0,20)
    # ax[ax_num].set_xlim(-delta_time,delta_time)
    for j in range(2):
        for i in range(3):
            ax[(i,j)].set_ylabel(r'Ion Mass [u]')
            ax[(i,j)].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
            ax[(i,j)].legend(loc = 'lower right')
            ax[(i,j)].axhline(y = 16, color = 'black', ls = '--',linewidth=1)
    
    ax[(0,0)].set_title(f'Dayside')
    ax[(0,1)].set_title(f'Nightside')
    ax[(2,0)].set_xlabel(f'Days since Dst minimum')
    ax[(2,1)].set_xlabel(f'Days since Dst minimum')
    
    # fig.legend(('SWARM A','SWARM B','SWARM C'),loc='center', bbox_to_anchor=(0.78, 0.52), ncol=3)

    plt.suptitle(f'Plots of efective ion mass for the {storm_name[ax_num]} storm (Orbital median)')
    # plt.gcf().autofmt_xdate()
    plt.tight_layout()
    # plt.savefig(f'storm_data/Plots/Decimal plot of {storm_name[ax_num]} storm.png')
    plt.show()


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

    # fig, ax = plt.subplots(2,1,figsize=(10, 5),)#sharex=True,) 
    # plot(file_names=name_list[0], dst_min=june_dst_min, ax_num = 0, column = 'M_i_eff')

    for i, element in enumerate([june_dst_min, december_dst_min, september_dst_min, august_dst_min]):
        fig, ax = plt.subplots(3,2,figsize=(25,15))#sharex=True,) 
        plot(file_names=name_list[i], dst_min=element, ax_num = i, column = 'M_i_eff')
        # plt.show()


    # fig, ax = plt.subplots(1,1,figsize=(10, 5),sharex=True,) 

    # for i, element in enumerate([june_dst_min, december_dst_min, september_dst_min, august_dst_min]):
    #     plot(file_names=name_list[i][:], dst_min=element, ax_num = i, column = 'N_i')

    # plt.show()
