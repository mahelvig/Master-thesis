import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import time
import matplotlib.ticker as ticker
import tqdm

from read_feather import data

def read_file(dir):
    #Function that takes a file (here/is/my/file_name) and returna a data frame
    df = data.read_feather(dir,dir)
    return df

    #Her vil jeg lage et program som plotter endringen i Ion effective mass ut fra baseline i forkant av stormen




# def plot_june_storm(self):
#     # Function that plots the june storm 

#     # Create dataframe from the saved data
#     df = data.read_feather(data.dir)


#     # Main phase
#     start_main  = pd.to_datetime('2015-06-22 19:00:00')
#     end_main    = pd.to_datetime('2015-06-23 04:30:00')


#     # Flag data
#     df = data.flag(df, start_main, end_main)
#     #Get the extracted dataframes
#     ngt_equ, day_equ = data.extract_data(df)

#     # Getting the MLT of the orbit
#     mean = []  
#     mean.append(round(ngt_equ["MLT"].mean()))
#     mean.append(round(day_equ["MLT"].mean()))
    

#     print('Plotting data:\n')
#     fig, ax = plt.subplots(2,1,sharex=True)

#     ax[0].scatter(ngt_equ['Timestamp'], ngt_equ['M_i_eff'], s= 0.2, marker = '.')
#     ax[1].scatter(day_equ['Timestamp'], day_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
#     #Plotting the daily median 
#     df.groupby(ngt_equ['Timestamp'].dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[0])
#     df.groupby(day_equ['Timestamp'].dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[1])

#     for i in range(len(ax)):
#         ax[i].set_ylabel('Ion Mass [u]')

#         ax[i].legend(loc = 'lower right')
#         ax[i].axvline(x = start_main, color = 'black', ls='--')
#         ax[i].axvline(x = end_main, color = 'black', ls='--')
#         ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
#         ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)

#     ax[0].set_ylim(0, 30)
#     ax[1].set_ylim(0,30 )
#     ax[0].set_title('Equatorial nightside')
#     ax[1].set_title('Equatorial dayside')
    
#     plt.gcf().autofmt_xdate()
#     fig.suptitle(f'Plot of effective ion mass during the June 2015 storm: SWARM {data.sat_name}')
#     plt.xlabel('Time')

#     #Maybe add a x lim to get the plots to equal length undependant from the available data?
#     storm_start = pd.to_datetime('2015-06-20')
#     storm_end   = pd.to_datetime('2015-06-26')
#     plt.xlim(storm_start,storm_end)
    
#     #Saves and shows the plot
#     print('\nSaving plot:', end="\r")
#     plt.savefig(f'storm_data/Plots/Plot of effective ion mass during the June 2015 storm sat_{data.sat_name}.png')
#     print('Plot saved. \n')
#     print('\nShowing plot:', end="\r")
    

# def plot_december_storm(self, dawn_dusk = False):
#     # Function that plots the december storm storm 

#     # Create dataframe from the saved data
#     df = data.read_feather(data.dir)

#     # Main phase
#     start_main  = pd.to_datetime('2015-12-22 04:00:00')
#     end_main    = pd.to_datetime('2015-12-22 23:00:00')

#     # Flag data
#     df = data.flag(df, start_main, end_main)

#     #Get the extracted dataframes
#     if dawn_dusk:
#         dawn_equ, dusk_equ = data.extract_data(df, dawn_dusk)

#         # Getting the MLT of the orbit
#         mean = []  
#         mean.append(round(dawn_equ["MLT"].mean()))
#         mean.append(round(dusk_equ["MLT"].mean()))

#         print('Plotting data:\n')
#         fig, ax = plt.subplots(2,1,sharex=True)

#         ax[0].scatter(dawn_equ['Timestamp'], dawn_equ['M_i_eff'], s= 0.2, marker = '.')
#         ax[1].scatter(dusk_equ['Timestamp'], dusk_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
#         #Plotting the daily median 
#         df.groupby(dawn_equ['Timestamp'].dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[0])
#         df.groupby(dusk_equ['Timestamp'].dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[1])
            
#         for i in range(len(ax)):
#             ax[i].set_ylabel('Ion Mass [u]')
#             ax[i].legend(loc = 'lower right')
#             ax[i].axvline(x = start_main, color = 'black', ls='--')
#             ax[i].axvline(x = end_main, color = 'black', ls='--')
#             ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4)) 
#             ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)


#         ax[0].set_ylim(0, 30)
#         ax[1].set_ylim(0,30 )
#         ax[0].set_title('Equatorial dawnside')
#         ax[1].set_title('Equatorial duskside')





#     else:
#         ngt_equ, day_equ = data.extract_data(df)

#         # Getting the MLT of the orbit
#         mean = []  
#         mean.append(round(ngt_equ["MLT"].mean()))
#         mean.append(round(day_equ["MLT"].mean()))


#         print('Plotting data:\n')
#         fig, ax = plt.subplots(2,1,sharex=True)

#         ax[0].scatter(ngt_equ['Timestamp'], ngt_equ['M_i_eff'], s= 0.2, marker = '.')
#         ax[1].scatter(day_equ['Timestamp'], day_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
#         #Plotting the daily median 
#         df.groupby(ngt_equ['Timestamp'].dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[0])
#         df.groupby(day_equ['Timestamp'].dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[1])
            
#         for i in range(len(ax)):
#             ax[i].set_ylabel('Ion Mass [u]')
#             ax[i].legend(loc = 'lower right')
#             ax[i].axvline(x = start_main, color = 'black', ls='--')
#             ax[i].axvline(x = end_main, color = 'black', ls='--')
#             ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4)) 
#             ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)


#         ax[0].set_ylim(0, 30)
#         ax[1].set_ylim(0,30 )
#         ax[0].set_title('Equatorial nightside')
#         ax[1].set_title('Equatorial dayside')
    
#     plt.gcf().autofmt_xdate()
#     fig.suptitle(f'Plot of effective ion mass during the December 2015 storm: SWARM {data.sat_name}')
#     plt.xlabel('Time')
    
#     #Maybe add a x lim to get the plots to equal length undependant from the available data?
#     storm_start = pd.to_datetime('2015-12-19')
#     storm_end   = pd.to_datetime('2015-12-27')
#     plt.xlim(storm_start,storm_end)
#     #Saves and shows the plot
#     print('\nSaving plot:', end="\r")
#     plt.savefig(f'storm_data/Plots/Plot of effective ion mass during the December 2015 storm sat_{data.sat_name}.png')
#     print('Plot saved. \n')
#     print('\nShowing plot:', end="\r")

    
# def plot_september_storm(self):
#     # Function that plots the december storm storm 

#     # Create dataframe from the saved data
#     df = data.read_feather(data.dir)

#     # Main phase
#     start_main  = pd.to_datetime('2017-09-08 03:00:00')
#     end_main    = pd.to_datetime('2017-09-08 23:50:00')

#     # Flag data
#     df = data.flag(df, start_main, end_main)

#     #Get the extracted dataframes
#     ngt_equ, day_equ = data.extract_data(df)

#     # Getting the MLT of the orbit
#     mean = []  
#     mean.append(round(ngt_equ["MLT"].mean()))
#     mean.append(round(day_equ["MLT"].mean()))

#     print('Plotting data:\n')
#     fig, ax = plt.subplots(2,1,sharex=True)

#     ax[0].scatter(ngt_equ['Timestamp'], ngt_equ['M_i_eff'], s= 0.2, marker = '.')
#     ax[1].scatter(day_equ['Timestamp'], day_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
#     #Plotting the daily median 
#     df.groupby(ngt_equ['Timestamp'].dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[0])
#     df.groupby(day_equ['Timestamp'].dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[1])
    
#     for i in range(len(ax)):
#         ax[i].set_ylabel('Ion Mass [u]')
#         ax[i].legend(loc = 'lower right')
#         ax[i].axvline(x = start_main, color = 'black', ls='--')
#         ax[i].axvline(x = end_main, color = 'black', ls='--')
#         ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
#         ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)


#     ax[0].set_ylim(0, 30)
#     ax[1].set_ylim(0,30 )
#     ax[0].set_title('Equatorial nightside')
#     ax[1].set_title('Equatorial dayside')
    
#     plt.gcf().autofmt_xdate()
#     fig.suptitle(f'Plot of effective ion mass during the September 2017 storm: SWARM {data.sat_name}')
#     plt.xlabel('Time')
    
#     #Maybe add a x lim to get the plots to equal length undependant from the available data?
#     storm_start = pd.to_datetime('2017-09-05')
#     storm_end   = pd.to_datetime('2017-09-11')
#     plt.xlim(storm_start,storm_end)
#     #Saves and shows the plot
#     print('\nSaving plot:', end="\r")
#     plt.savefig(f'storm_data/Plots/Plot of effective ion mass during the September 2017 storm sat_{data.sat_name}.png')
#     print('Plot saved. \n')
#     print('\nShowing plot:', end="\r")
    

# def plot_august_storm(self):
#     # Function that plots the august storm storm 

#     # Create dataframe from the saved data
#     df = data.read_feather(data.dir)


#     # Main phase
#     start_main  = pd.to_datetime('2018-08-25 13:15:00')
#     end_main    = pd.to_datetime('2018-08-26 10:00:00')

#     # Flag data
#     df = data.flag(df, start_main, end_main)

#     #Get the extracted dataframes
#     ngt_equ, day_equ = data.extract_data(df)

#     # Getting the MLT of the orbit
#     mean = []  
#     mean.append(round(ngt_equ["MLT"].mean()))
#     mean.append(round(day_equ["MLT"].mean()))

#     print('Plotting data:\n')
#     fig, ax = plt.subplots(2,1,sharex=True)

#     ax[0].scatter(ngt_equ['Timestamp'], ngt_equ['M_i_eff'], s= 0.2, marker = '.')
#     ax[1].scatter(day_equ['Timestamp'], day_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
#     #Plotting the daily median 
#     df.groupby(ngt_equ['Timestamp'].dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[0])
#     df.groupby(day_equ['Timestamp'].dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[1])
    
#     for i in range(len(ax)):
#         ax[i].set_ylabel('Ion Mass [u]')
#         ax[i].legend(loc = 'lower right')
#         ax[i].axvline(x = start_main, color = 'black', ls='--')
#         ax[i].axvline(x = end_main, color = 'black', ls='--')
#         ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
#         ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)

                
#     ax[0].set_ylim(0,30)
#     ax[1].set_ylim(0,30)
#     ax[0].set_title('Equatorial nightside')
#     ax[1].set_title('Equatorial dayside')
    
#     plt.gcf().autofmt_xdate()
#     fig.suptitle(f'Plot of effective ion mass during the August 2018 storm: SWARM {data.sat_name}')
#     plt.xlabel('Time')
    
#     #Maybe add a x lim to get the plots to equal length undependant from the available data?
#     storm_start = pd.to_datetime('2018-08-23')
#     storm_end   = pd.to_datetime('2018-08-29')
#     plt.xlim(storm_start,storm_end)
#     #Saves and shows the plot
#     print('\nSaving plot:', end="\r")
#     plt.savefig(f'storm_data/Plots/Plot of effective ion mass during the August 2018 storm sat_{data.sat_name}.png')
#     print('Plot saved. \n')
#     print('\nShowing plot:', end="\r")
    


if __name__ == '__main__':
    dir         = 'storm_data/Storms/'
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
    var_names   = [june_A, june_B, june_C, december_A, december_B, december_C, 
                   september_A, september_B, september_C, august_A, august_B, august_C]

    for dir in var_names:
        df = read_file(dir)