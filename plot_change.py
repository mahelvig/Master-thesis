import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import time
import matplotlib.ticker as ticker
import tqdm

### Program very similar to read_feather.py but plots the change that happens 
### during the storm by substracting a computed baseline mean from the calm
### week before the storm initiates


class changes:
    def __init__(self,dir, baseline_value_night, baseline_value_day):

        self.dir = dir
        # Number of hours to plot median
        self.n_hour = 6
        # Baseline value from the week before the storm
        self.baseline_value_night   = baseline_value_night   
        self.baseline_value_day     = baseline_value_day
        if dir[-1]=='A':
            self.sat_name = 'A'
        elif dir[-1]=='B':
            self.sat_name = 'B'
        elif dir[-1]=='C':
            self.sat_name = 'C'
        else:
            print('Warning: Directory does not include the name of the satellite.\nself.sat_name does not exist.')

    def read_feather(self, dir):
        #Function that reads a feather data file and returns it as a dataframe
        print(f'\nReading {dir}:\n')
        df = pd.read_feather(dir)
        df.set_index('Timestamp', inplace=True)
        # Masking where ion mass is manually set to -1
        df = df.mask(df['M_i_eff']==-1)
        print(f'\nReading complete.\n')
        return df

    def flag(self, df, start_main=None, end_main=None, end_recovery = None):
        #Function that finds where the orbit of the satellites was and flags it
        #Takes the dataframe and the start and end of the main and recovery phase as arguments

        # New colonm in df for new flags
        df['Costom_Flags'] = 0
        print('\nApplying flags:\n')
        # Locates where the satellite orbit is on the dayside and adds 2 as a flag
        df.loc[(df['MLT'] >= 8) & (df['MLT'] <= 16), 'Costom_Flags'] += 2
        # Locates where the satellite orbit is on the nightside and adds 4 as a flag
        df.loc[(df['MLT'] >= 20) | (df['MLT'] <= 4), 'Costom_Flags'] += 4
        # Locates where the satellite orbit is in the polar region and adds 8 as a flag
        df.loc[(df['QDLatitude'] > 60) | (df['QDLatitude'] < -60), 'Costom_Flags'] += 8
        # Locates where the satellite orbit is in the equatorial region and adds 16 as a flag
        df.loc[(df['QDLatitude'] >= -15) & (df['QDLatitude'] <= 15), 'Costom_Flags'] += 16


        # Locates where the data was in the main phase of the storm
        if start_main != None and end_main != None:
            df.loc[(df.index > start_main) & (df.index < end_main), 'Costom_Flags'] += 32
        # Locates where the data was in the recovery phase of the storm
        if end_recovery != None and end_main != None:
            df.loc[(df.index > end_main) & (df.index < end_recovery), 'Costom_Flags'] += 64

        # Locates where the satellite orbit is on the dawnside and adds 128 as a flag
        df.loc[(df['MLT'] < 8) & (df['MLT'] > 4), 'Costom_Flags'] += 128
        # Locates where the satellite orbit is on the duskside and adds 256 as a flag
        df.loc[(df['MLT'] < 20) & (df['MLT'] > 16), 'Costom_Flags'] += 256
        return df


    def extract_data(self, df, dawn_dusk = False):
        #Statement that results in True when the data is in the equatorial region 
        # and on the dayside/nightside
             
        flags_day           = (df['Costom_Flags']& 2 == 2)
        flags_night         = (df['Costom_Flags']& 4 == 4)
        flags_polar         = (df['Costom_Flags']& 8 == 8)
        flags_equatorial    = (df['Costom_Flags']& 16== 16)
        #Using already existing flags for latitudal validity:
        # flags_equatorial    = (df['M_i_eff_Flags']& 64== 64)
        flags_main_phase    = (df['Costom_Flags']& 32== 32)
        flags_recovery_phase= (df['Costom_Flags']& 64== 64)
        flags_dawn          = (df['Costom_Flags']& 128== 128)
        flags_dusk          = (df['Costom_Flags']& 256== 256)
        
        #Defining new dataframes with wanted flags 
        day_equ     = df.where(flags_day    & flags_equatorial  )
        ngt_equ     = df.where(flags_night  & flags_equatorial  )
        # day_equ     = df.mask(flags_equatorial  )
        # day_equ     = df.where(flags_day )

        # ngt_equ     = df.where(flags_night  )
        # ngt_equ     = df.mask(flags_equatorial    )
        dawn_equ    = df.where(flags_dawn    & flags_equatorial  )
        dusk_equ    = df.where(flags_dusk    & flags_equatorial  )
        if dawn_dusk:
            return dawn_equ, dusk_equ
        else:
            return ngt_equ, day_equ


    def plot_june_storm(self):
        # Function that plots the june storm 

        # Create dataframe from the saved data
        df = self.read_feather(self.dir)

        # Main phase
        start_main  = pd.to_datetime('2015-06-22 19:00:00')
        end_main    = pd.to_datetime('2015-06-23 04:30:00')


        # Flag data
        df = self.flag(df, start_main, end_main)
        #Get the extracted dataframes
        ngt_equ, day_equ = self.extract_data(df)

        # Resample by 3 hourly median
        ngt_equ_resampled = ngt_equ['M_i_eff'].resample(f'{self.n_hour}H').mean()
        day_equ_resampled = day_equ['M_i_eff'].resample(f'{self.n_hour}H').mean()
        print(ngt_equ_resampled, day_equ_resampled)
        ngt_equ_resampled = ngt_equ_resampled - self.baseline_value_night
        day_equ_resampled = day_equ_resampled - self.baseline_value_day
    
        # Getting the MLT of the orbit
        mean = []  
        mean.append(round(ngt_equ["MLT"].mean()))
        mean.append(round(day_equ["MLT"].mean()))
        

        print('Plotting data:\n')
        fig, ax = plt.subplots(2,1,sharex=True)

        # ax[0].scatter(ngt_equ.index, ngt_equ['M_i_eff'], s= 0.2, marker = '.')
        # ax[1].scatter(day_equ.index, day_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
        #Plotting the daily median 
        # df.rolling(3).median().plot(y='M_i_eff',kind="line", color = 'tab:red', label = 'Something median', ax=ax[0])
        # df.rolling(3).median().plot(y='M_i_eff',kind="line", color = 'tab:red', label = 'Daily median', ax=ax[1])
        ax[0].plot(ngt_equ_resampled, color = 'tab:red', label = f'{self.n_hour} hour median')
        ax[1].plot(day_equ_resampled, color = 'tab:red', label = f'{self.n_hour} hour median')


        for i in range(len(ax)):
            ax[i].set_ylabel('Ion Mass [u]')
    
            ax[i].legend(loc = 'lower right')
            ax[i].axvline(x = start_main, color = 'black', ls='--')
            ax[i].axvline(x = end_main, color = 'black', ls='--')
            ax[i].axhline(y = 0, color = 'black', ls = '--')
            ax[i].axhline(y = 0, color = 'black', ls='--')
            ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
            ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)

        # ax[0].set_ylim(-5,5)
        # ax[1].set_ylim(-2,2)
        ax[0].set_title('Equatorial nightside')
        ax[1].set_title('Equatorial dayside')
       
        plt.gcf().autofmt_xdate()
        fig.suptitle(f'Changes in effective ion mass during the June 2015 storm: SWARM {self.sat_name}')
        plt.xlabel('Time')

        #Maybe add a x lim to get the plots to equal length undependant from the available data?
        storm_start = pd.to_datetime('2015-06-20')
        storm_end   = pd.to_datetime('2015-06-26')
        plt.xlim(storm_start,storm_end)
        
        #Saves and shows the plot
        print('\nSaving plot:', end="\r")
        plt.savefig(f'storm_data/Plots/KOPI-Changes in effective ion mass during the 2015-06 storm sat_{self.sat_name}.png')
        # plt.show()
        print('Plot saved. \n')
        print('\nShowing plot:', end="\r")
        

    def plot_december_storm(self, dawn_dusk = False):
        # Function that plots the december storm storm 

        # Create dataframe from the saved data
        df = self.read_feather(self.dir)

        # Main phase
        start_main  = pd.to_datetime('2015-12-20 04:00:00')
        end_main    = pd.to_datetime('2015-12-20 23:00:00')

        # Flag data
        df = self.flag(df, start_main, end_main)

        #Get the extracted dataframes
        if dawn_dusk:
            dawn_equ, dusk_equ = self.extract_data(df, dawn_dusk)

            # Resample by 3 hourly median
            dawn_equ_resampled = dawn_equ['M_i_eff'].resample(f'{self.n_hour}H').mean()
            dusk_equ_resampled = dusk_equ['M_i_eff'].resample(f'{self.n_hour}H').mean()
            print(dawn_equ_resampled, dusk_equ_resampled)
            dawn_equ_resampled = dawn_equ_resampled - self.baseline_value_night
            dusk_equ_resampled = dusk_equ_resampled - self.baseline_value_day

            # Getting the MLT of the orbit
            mean = []  
            mean.append(round(dawn_equ["MLT"].mean()))
            mean.append(round(dusk_equ["MLT"].mean()))

            print('Plotting data:\n')
            fig, ax = plt.subplots(2,1,sharex=True)

            # ax[0].scatter(dawn_equ.index, dawn_equ['M_i_eff'], s= 0.2, marker = '.')
            # ax[1].scatter(dusk_equ.index, dusk_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
            #Plotting the daily median 
            # df.groupby(dawn_equ.index.dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[0])
            # df.groupby(dusk_equ.index.dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[1])
            ax[0].plot(dawn_equ_resampled, color = 'tab:red', label = f'{self.n_hour} hour median')
            ax[1].plot(dusk_equ_resampled, color = 'tab:red', label = f'{self.n_hour} hour median')

            for i in range(len(ax)):
                ax[i].set_ylabel('Ion Mass [u]')
                ax[i].legend(loc = 'lower right')
                ax[i].axvline(x = start_main, color = 'black', ls='--')
                ax[i].axvline(x = end_main, color = 'black', ls='--')
                ax[i].axhline(y = 0, color = 'black', ls = '--')
                ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4)) 
                ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)


            # ax[0].set_ylim(-5,5)
            # ax[1].set_ylim(-2,2)
            ax[0].set_title('Equatorial dawnside')
            ax[1].set_title('Equatorial duskside')





        else:
            ngt_equ, day_equ = self.extract_data(df)
            # Resample by 3 hourly median
            ngt_equ_resampled = ngt_equ['M_i_eff'].resample(f'{self.n_hour}H').mean()
            day_equ_resampled = day_equ['M_i_eff'].resample(f'{self.n_hour}H').mean()
            print(ngt_equ_resampled, day_equ_resampled)
            ngt_equ_resampled = ngt_equ_resampled - self.baseline_value_night
            day_equ_resampled = day_equ_resampled - self.baseline_value_day



            # Getting the MLT of the orbit
            mean = []  
            mean.append(round(ngt_equ["MLT"].mean()))
            mean.append(round(day_equ["MLT"].mean()))


            print('Plotting data:\n')
            fig, ax = plt.subplots(2,1,sharex=True)

            # ax[0].scatter(ngt_equ.index, ngt_equ['M_i_eff'], s= 0.2, marker = '.')
            # ax[1].scatter(day_equ.index, day_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
            #Plotting the daily median 
            # df.groupby(ngt_equ.index.dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[0])
            # df.groupby(day_equ.index.dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[1])
            ax[0].plot(ngt_equ_resampled, color = 'tab:red', label = f'{self.n_hour} hour median')
            ax[1].plot(day_equ_resampled, color = 'tab:red', label = f'{self.n_hour} hour median')
                
            for i in range(len(ax)):
                ax[i].set_ylabel('Ion Mass [u]')
                ax[i].legend(loc = 'lower right')
                ax[i].axvline(x = start_main, color = 'black', ls='--')
                ax[i].axvline(x = end_main, color = 'black', ls='--')
                ax[i].axhline(y = 0, color = 'black', ls = '--')
                ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4)) 
                ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)


            # ax[0].set_ylim(-5,5)
            # ax[1].set_ylim(-2,2)
            ax[0].set_title('Equatorial nightside')
            ax[1].set_title('Equatorial dayside')
       
        plt.gcf().autofmt_xdate()
        fig.suptitle(f'Changes in effective ion mass during the December 2015 storm: SWARM {self.sat_name}')
        plt.xlabel('Time')
        
        #Maybe add a x lim to get the plots to equal length undependant from the available data?
        storm_start = pd.to_datetime('2015-12-17')
        storm_end   = pd.to_datetime('2015-12-23')
        plt.xlim(storm_start,storm_end)
        #Saves and shows the plot
        print('\nSaving plot:', end="\r")
        plt.savefig(f'storm_data/Plots/KOPI-Changes in effective ion mass during the 2015-12 storm sat_{self.sat_name}.png')
        print('Plot saved. \n')
        print('\nShowing plot:', end="\r")

        
    def plot_september_storm(self):
        # Function that plots the december storm storm 

        # Create dataframe from the saved data
        df = self.read_feather(self.dir)

        # Main phase
        start_main  = pd.to_datetime('2017-09-08 03:00:00')
        end_main    = pd.to_datetime('2017-09-08 23:50:00')

        # Flag data
        df = self.flag(df, start_main, end_main)

        #Get the extracted dataframes
        ngt_equ, day_equ = self.extract_data(df)

        # Resample by 3 hourly median
        ngt_equ_resampled = ngt_equ['M_i_eff'].resample(f'{self.n_hour}H').mean()
        day_equ_resampled = day_equ['M_i_eff'].resample(f'{self.n_hour}H').mean()
        print(ngt_equ_resampled, day_equ_resampled)
        ngt_equ_resampled = ngt_equ_resampled - self.baseline_value_night
        day_equ_resampled = day_equ_resampled - self.baseline_value_day



        # Getting the MLT of the orbit
        mean = []  
        mean.append(round(ngt_equ["MLT"].mean()))
        mean.append(round(day_equ["MLT"].mean()))

        print('Plotting data:\n')
        fig, ax = plt.subplots(2,1,sharex=True)

        # ax[0].scatter(ngt_equ.index, ngt_equ['M_i_eff'], s= 0.2, marker = '.')
        # ax[1].scatter(day_equ.index, day_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
        #Plotting the daily median 
        # df.groupby(ngt_equ.index.dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[0])
        # df.groupby(day_equ.index.dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[1])
        ax[0].plot(ngt_equ_resampled, color = 'tab:red', label = f'{self.n_hour} hour median')
        ax[1].plot(day_equ_resampled, color = 'tab:red', label = f'{self.n_hour} hour median')
        
        for i in range(len(ax)):
            ax[i].set_ylabel('Ion Mass [u]')
            ax[i].legend(loc = 'lower right')
            ax[i].axvline(x = start_main, color = 'black', ls='--')
            ax[i].axvline(x = end_main, color = 'black', ls='--')
            ax[i].axhline(y = 0, color = 'black', ls = '--')
            ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
            ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)


        # ax[0].set_ylim(-5,5)
        # ax[1].set_ylim(-2,2)
        ax[0].set_title('Equatorial nightside')
        ax[1].set_title('Equatorial dayside')
       
        plt.gcf().autofmt_xdate()
        fig.suptitle(f'Changes in effective ion mass during the September 2017 storm: SWARM {self.sat_name}')
        plt.xlabel('Time')
        
        #Maybe add a x lim to get the plots to equal length undependant from the available data?
        storm_start = pd.to_datetime('2017-09-05')
        storm_end   = pd.to_datetime('2017-09-11')
        plt.xlim(storm_start,storm_end)
        #Saves and shows the plot
        print('\nSaving plot:', end="\r")
        plt.savefig(f'storm_data/Plots/KOPI-Changes in effective ion mass during the 2017-09 storm sat_{self.sat_name}.png')
        print('Plot saved. \n')
        print('\nShowing plot:', end="\r")
        

    def plot_august_storm(self):
        # Function that plots the august storm storm 

        # Create dataframe from the saved data
        df = self.read_feather(self.dir)


        # Main phase
        start_main  = pd.to_datetime('2018-08-25 13:15:00')
        end_main    = pd.to_datetime('2018-08-26 10:00:00')

        # Flag data
        df = self.flag(df, start_main, end_main)

        #Get the extracted dataframes
        ngt_equ, day_equ = self.extract_data(df)

        # Resample by 3 hourly median
        ngt_equ_resampled = ngt_equ['M_i_eff'].resample(f'{self.n_hour}H').mean()
        day_equ_resampled = day_equ['M_i_eff'].resample(f'{self.n_hour}H').mean()
        print(ngt_equ_resampled, day_equ_resampled)
        ngt_equ_resampled = ngt_equ_resampled - self.baseline_value_night
        day_equ_resampled = day_equ_resampled - self.baseline_value_day



        # Getting the MLT of the orbit
        mean = []  
        mean.append(round(ngt_equ["MLT"].mean()))
        mean.append(round(day_equ["MLT"].mean()))

        print('Plotting data:\n')
        fig, ax = plt.subplots(2,1,sharex=True)

        # ax[0].scatter(ngt_equ.index, ngt_equ['M_i_eff'], s= 0.2, marker = '.')
        # ax[1].scatter(day_equ.index, day_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
        #Plotting the daily median 
        # df.groupby(ngt_equ.index.dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[0])
        # df.groupby(day_equ.index.dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[1])
        ax[0].plot(ngt_equ_resampled, color = 'tab:red', label = f'{self.n_hour} hour median')
        ax[1].plot(day_equ_resampled, color = 'tab:red', label = f'{self.n_hour} hour median')
        
        for i in range(len(ax)):
            ax[i].set_ylabel('Ion Mass [u]')
            ax[i].legend(loc = 'lower right')
            ax[i].axvline(x = start_main, color = 'black', ls='--')
            ax[i].axvline(x = end_main, color = 'black', ls='--')
            ax[i].axhline(y = 0, color = 'black', ls = '--')
            ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
            ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)

                   
        # ax[0].set_ylim(-5,5)
        # ax[1].set_ylim(-2,2)
        ax[0].set_title('Equatorial nightside')
        ax[1].set_title('Equatorial dayside')
       
        plt.gcf().autofmt_xdate()
        fig.suptitle(f'Changes in effective ion mass during the August 2018 storm: SWARM {self.sat_name}')
        plt.xlabel('Time')
        
        #Maybe add a x lim to get the plots to equal length undependant from the available data?
        storm_start = pd.to_datetime('2018-08-23')
        storm_end   = pd.to_datetime('2018-08-29')
        plt.xlim(storm_start,storm_end)
        #Saves and shows the plot
        print('\nSaving plot:', end="\r")
        plt.savefig(f'storm_data/Plots/KOPI-Changes in effective ion mass during the 2018-08 storm sat_{self.sat_name}.png')
        print('Plot saved. \n')
        print('\nShowing plot:', end="\r")
        
    def plot_baseline(self, dawn_dusk = False, title = None):
        # Function that plots the baselines 

        # Create dataframe from the saved data
        df = self.read_feather(self.dir) 

        # Flag data
        df = self.flag(df)


        if dawn_dusk:
            #Get the extracted dataframes
            dawn_equ, dusk_equ = self.extract_data(df, dawn_dusk)

            # Getting the MLT of the orbit
            mean = []  
            mean.append(round(dawn_equ["MLT"].mean()))
            mean.append(round(dusk_equ["MLT"].mean()))

            print('Plotting data:\n')
            fig, ax = plt.subplots(2,1,sharex=True)

            ax[0].scatter(dawn_equ.index, dawn_equ['M_i_eff'], s= 0.2, marker = '.')
            ax[1].scatter(dusk_equ.index, dusk_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
            #Plotting the daily median 
            df.groupby(dawn_equ.index.dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[0])
            df.groupby(dusk_equ.index.dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[1])
                
            for i in range(len(ax)):
                ax[i].set_ylabel('Ion Mass [u]')
                ax[i].legend(loc = 'lower right')
                ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4)) 
                ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)

            # ax[0].set_ylim(0, 30)
            # ax[1].set_ylim(0,30 )
            ax[0].set_title('Equatorial dawnside')
            ax[1].set_title('Equatorial duskside')
        else:
            #Get the extracted dataframes
            ngt_equ, day_equ = self.extract_data(df)
            
            # Getting the MLT of the orbit
            mean = []  
            mean.append(round(ngt_equ["MLT"].mean()))
            mean.append(round(day_equ["MLT"].mean()))

            print('Plotting data:\n')
            fig, ax = plt.subplots(2,1,sharex=True)

            ax[0].scatter(ngt_equ.index, ngt_equ['M_i_eff'], s= 0.2, marker = '.')
            ax[1].scatter(day_equ.index, day_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
            #Plotting the daily median 
            df.groupby(ngt_equ.index.dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[0])
            df.groupby(day_equ.index.dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[1])
            
            for i in range(len(ax)):
                ax[i].set_ylabel('Ion Mass [u]')
                ax[i].legend(loc = 'lower right')
                ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
                ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)

                    
            # ax[0].set_ylim(0,30)
            # ax[1].set_ylim(0,30)
            ax[0].set_title('Equatorial nightside')
            ax[1].set_title('Equatorial dayside')
       
        plt.gcf().autofmt_xdate()
        fig.suptitle(f'Baseline plot {title}: SWARM {self.sat_name}')
        plt.xlabel('Time')

        #Saving the baseline mean for use in later plots
        np.save(f'storm_data/mean/mean_{title}_{self.sat_name}',mean,allow_pickle=True)
        
        #Saves and shows the plot
        print('\nSaving plot:', end="\r")
        plt.savefig(f'storm_data/Plots/Baseline plot of effective ion mass {title} sat_{self.sat_name}.png')
        print('Plot saved. \n')
        print('\nShowing plot:', end="\r")
        plt.close()



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

    start_time      = time.time()
    #Creating objects for the June 2015 storm
    june_storm_A    = changes(dir+june_A,baseline_value_night = 15.30, baseline_value_day = 19.09)
    june_storm_B    = changes(dir+june_B,baseline_value_night = 11.21, baseline_value_day = 18.88)
    june_storm_C    = changes(dir+june_C,baseline_value_night = 14.40, baseline_value_day = 18.08)
    june_storm_A.plot_june_storm()
    june_storm_B.plot_june_storm()
    june_storm_C.plot_june_storm()

    #Creating objects for the December 2015 storm
    december_storm_A    = changes(dir+december_A,baseline_value_night = 18.17, baseline_value_day = 17.30)
    december_storm_B    = changes(dir+december_B,baseline_value_night = 13.10, baseline_value_day = 17.66)
    december_storm_C    = changes(dir+december_C,baseline_value_night = 17.45, baseline_value_day = 16.01)
    december_storm_A.plot_december_storm(dawn_dusk=True)
    december_storm_B.plot_december_storm()
    december_storm_C.plot_december_storm(dawn_dusk=True)

    #Creating objects for the September 2017 storm
    september_storm_A    = changes(dir+september_A,baseline_value_night = 11.31, baseline_value_day = 16.10)
    september_storm_B    = changes(dir+september_B,baseline_value_night = 04.18, baseline_value_day = 15.05)
    september_storm_C    = changes(dir+september_C,baseline_value_night = 11.08, baseline_value_day = 15.61)
    september_storm_A.plot_september_storm()
    september_storm_B.plot_september_storm()
    september_storm_C.plot_september_storm()

    #Creating objects for the August 2018 storm
    august_storm_A    = changes(dir+august_A,baseline_value_night = 04.68, baseline_value_day = 14.05)
    august_storm_B    = changes(dir+august_B,baseline_value_night = 02.99, baseline_value_day = 06.38)
    august_storm_C    = changes(dir+august_C,baseline_value_night = 07.09, baseline_value_day = 13.73)
    august_storm_A.plot_august_storm()
    august_storm_B.plot_august_storm()
    august_storm_C.plot_august_storm()


    end_time        = time.time()
    print(f'Program complete. Elapesed time: {end_time-start_time:.2f} seconds.')



# start_time  = time.time()       
# df          = pd.read_feather(dir+name)
# end_time    = time.time()
# print(f'Elapsed time is {end_time-start_time:.2f} seconds.')


# #Sanity check 
# start_date  = '2015-06-21'
# end_date    = '2015-06-23'
# sanity_check_df = df[(df.index >= start_date) & (df.index <= end_date)]


# start_time  = time.time()       
# df2         = pd.read_feather(dir+name2)
# end_time    = time.time()
# print(f'Elapsed time is {end_time-start_time:.2f} seconds.')


# start_date  = '2015-12-18'
# end_date    = '2015-12-30'
# df3 = df2[(df2.index >= start_date) & (df2.index <= end_date)]


# plt.figure(1)
# plt.scatter(sanity_check_df.index,sanity_check_df['M_i_eff'], s= 0.2, marker = '.')
# plt.gcf().autofmt_xdate()
# plt.title('Plot of the same dates as article. Used as sanity check.')
# plt.xlabel('Time')
# plt.ylabel('Ion Mass [u]')
# plt.ylim(0,25)

# plt.figure(2)
# plt.scatter(df3.index,df3['M_i_eff'], s= 0.2, marker = '.')
# plt.gcf().autofmt_xdate()
# plt.title('Plot ')
# plt.xlabel('Time')
# plt.ylabel('Ion Mass [u]')
# plt.ylim(0,25)



