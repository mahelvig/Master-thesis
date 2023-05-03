import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import time
import matplotlib.ticker as ticker
import tqdm


class plotting:
    def __init__(self,dir):

        self.dir = dir
        # Number of hours to plot median
        self.n_hour = 3
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


    def extract_data(self, df, dawn_dusk = False, return_mean = False):
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
            if return_mean:
                dawn_equ_mean, dusk_equ_mean = dawn_equ['M_i_eff'].median(), dusk_equ['M_i_eff'].median() 
                print(dawn_equ_mean, dusk_equ_mean)
            return dawn_equ, dusk_equ
        else:
            if return_mean:
                ngt_equ_mean, day_equ_mean = ngt_equ['M_i_eff'].median(), day_equ['M_i_eff'].median() 
                print(ngt_equ_mean, day_equ_mean)
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
        ngt_equ_resampled = ngt_equ['M_i_eff'].resample(f'{self.n_hour}H').median()
        day_equ_resampled = day_equ['M_i_eff'].resample(f'{self.n_hour}H').median()
        # Getting the MLT of the orbit
        mean = []  
        mean.append(round(ngt_equ["MLT"].mean()))
        mean.append(round(day_equ["MLT"].mean()))
        

        print('Plotting data:\n')
        fig, ax = plt.subplots(2,1,sharex=True)

        ax[0].scatter(ngt_equ.index, ngt_equ['M_i_eff'], s= 0.2, marker = '.')
        ax[1].scatter(day_equ.index, day_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
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
            ax[i].axhline(y = 16, color = 'black', ls = '--',linewidth=1)
            ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
            ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)

        ax[0].set_ylim(0, 30)
        ax[1].set_ylim(0,30 )
        ax[0].set_title('Equatorial nightside')
        ax[1].set_title('Equatorial dayside')
       
        plt.gcf().autofmt_xdate()
        fig.suptitle(f'Plot of effective ion mass during the June 2015 storm: Swarm {self.sat_name}')
        plt.xlabel('Time')

        #Maybe add a x lim to get the plots to equal length undependant from the available data?
        storm_start = pd.to_datetime('2015-06-20')
        storm_end   = pd.to_datetime('2015-06-26')
        plt.xlim(storm_start,storm_end)
        
        #Saves and shows the plot
        print('\nSaving plot:', end="\r")
        plt.savefig(f'storm_data/Plots/Plot of effective ion mass during the 2015-06 storm sat_{self.sat_name}.png')
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
            dawn_equ_resampled = dawn_equ['M_i_eff'].resample(f'{self.n_hour}H').median()
            dusk_equ_resampled = dusk_equ['M_i_eff'].resample(f'{self.n_hour}H').median()

            # Getting the MLT of the orbit
            mean = []  
            mean.append(round(dawn_equ["MLT"].mean()))
            mean.append(round(dusk_equ["MLT"].mean()))

            print('Plotting data:\n')
            fig, ax = plt.subplots(2,1,sharex=True)

            ax[0].scatter(dawn_equ.index, dawn_equ['M_i_eff'], s= 0.2, marker = '.')
            ax[1].scatter(dusk_equ.index, dusk_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
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
                ax[i].axhline(y = 16, color = 'black', ls = '--',linewidth=1)
                ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4)) 
                ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)


            ax[0].set_ylim(0, 30)
            ax[1].set_ylim(0,30 )
            ax[0].set_title('Equatorial dawnside')
            ax[1].set_title('Equatorial duskside')





        else:
            ngt_equ, day_equ = self.extract_data(df)
            # Resample by 3 hourly median
            ngt_equ_resampled = ngt_equ['M_i_eff'].resample(f'{self.n_hour}H').median()
            day_equ_resampled = day_equ['M_i_eff'].resample(f'{self.n_hour}H').median()
            # Getting the MLT of the orbit
            mean = []  
            mean.append(round(ngt_equ["MLT"].mean()))
            mean.append(round(day_equ["MLT"].mean()))


            print('Plotting data:\n')
            fig, ax = plt.subplots(2,1,sharex=True)

            ax[0].scatter(ngt_equ.index, ngt_equ['M_i_eff'], s= 0.2, marker = '.')
            ax[1].scatter(day_equ.index, day_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
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
                ax[i].axhline(y = 16, color = 'black', ls = '--',linewidth=1)
                ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4)) 
                ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)


            ax[0].set_ylim(0, 30)
            ax[1].set_ylim(0,30 )
            ax[0].set_title('Equatorial nightside')
            ax[1].set_title('Equatorial dayside')
       
        plt.gcf().autofmt_xdate()
        fig.suptitle(f'Plot of effective ion mass during the December 2015 storm: Swarm {self.sat_name}')
        plt.xlabel('Time')
        
        #Maybe add a x lim to get the plots to equal length undependant from the available data?
        storm_start = pd.to_datetime('2015-12-17')
        storm_end   = pd.to_datetime('2015-12-23')
        plt.xlim(storm_start,storm_end)
        #Saves and shows the plot
        print('\nSaving plot:', end="\r")
        plt.savefig(f'storm_data/Plots/Plot of effective ion mass during the 2015-12 storm sat_{self.sat_name}.png')
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
        ngt_equ_resampled = ngt_equ['M_i_eff'].resample(f'{self.n_hour}H').median()
        day_equ_resampled = day_equ['M_i_eff'].resample(f'{self.n_hour}H').median()

        # Getting the MLT of the orbit
        mean = []  
        mean.append(round(ngt_equ["MLT"].mean()))
        mean.append(round(day_equ["MLT"].mean()))

        print('Plotting data:\n')
        fig, ax = plt.subplots(2,1,sharex=True)

        ax[0].scatter(ngt_equ.index, ngt_equ['M_i_eff'], s= 0.2, marker = '.')
        ax[1].scatter(day_equ.index, day_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
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
            ax[i].axhline(y = 16, color = 'black', ls = '--',linewidth=1)
            ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
            ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)


        ax[0].set_ylim(0, 30)
        ax[1].set_ylim(0,30 )
        ax[0].set_title('Equatorial nightside')
        ax[1].set_title('Equatorial dayside')
       
        plt.gcf().autofmt_xdate()
        fig.suptitle(f'Plot of effective ion mass during the September 2017 storm: Swarm {self.sat_name}')
        plt.xlabel('Time')
        
        #Maybe add a x lim to get the plots to equal length undependant from the available data?
        storm_start = pd.to_datetime('2017-09-05')
        storm_end   = pd.to_datetime('2017-09-11')
        plt.xlim(storm_start,storm_end)
        #Saves and shows the plot
        print('\nSaving plot:', end="\r")
        plt.savefig(f'storm_data/Plots/Plot of effective ion mass during the 2017-09 storm sat_{self.sat_name}.png')
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
        ngt_equ_resampled = ngt_equ['M_i_eff'].resample(f'{self.n_hour}H').median()
        day_equ_resampled = day_equ['M_i_eff'].resample(f'{self.n_hour}H').median()

        # Getting the MLT of the orbit
        mean = []  
        mean.append(round(ngt_equ["MLT"].mean()))
        mean.append(round(day_equ["MLT"].mean()))

        print('Plotting data:\n')
        fig, ax = plt.subplots(2,1,sharex=True)

        ax[0].scatter(ngt_equ.index, ngt_equ['M_i_eff'], s= 0.2, marker = '.')
        ax[1].scatter(day_equ.index, day_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
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
            ax[i].axhline(y = 16, color = 'black', ls = '--',linewidth=1)
            ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
            ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)

                   
        ax[0].set_ylim(0,30)
        ax[1].set_ylim(0,30)
        ax[0].set_title('Equatorial nightside')
        ax[1].set_title('Equatorial dayside')
       
        plt.gcf().autofmt_xdate()
        fig.suptitle(f'Plot of effective ion mass during the August 2018 storm: Swarm {self.sat_name}')
        plt.xlabel('Time')
        
        #Maybe add a x lim to get the plots to equal length undependant from the available data?
        storm_start = pd.to_datetime('2018-08-23')
        storm_end   = pd.to_datetime('2018-08-29')
        plt.xlim(storm_start,storm_end)
        #Saves and shows the plot
        print('\nSaving plot:', end="\r")
        plt.savefig(f'storm_data/Plots/Plot of effective ion mass during the 2018-08 storm sat_{self.sat_name}.png')
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
            dawn_equ, dusk_equ = self.extract_data(df, dawn_dusk, return_mean=True)
            # Resample by 3 hourly median
            dawn_equ_resampled = dawn_equ['M_i_eff'].resample(f'{self.n_hour}H').median()
            dusk_equ_resampled = dusk_equ['M_i_eff'].resample(f'{self.n_hour}H').median()


            # Getting the MLT of the orbit
            mean = []  
            mean.append(round(dawn_equ["MLT"].mean()))
            mean.append(round(dusk_equ["MLT"].mean()))

            print('Plotting data:\n')
            fig, ax = plt.subplots(2,1,sharex=True)

            ax[0].scatter(dawn_equ.index, dawn_equ['M_i_eff'], s= 0.2, marker = '.')
            ax[1].scatter(dusk_equ.index, dusk_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
            #Plotting the daily median 
            # df.groupby(dawn_equ.index.dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[0])
            # df.groupby(dusk_equ.index.dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[1])
            ax[0].plot(dawn_equ_resampled, color = 'tab:red', label = f'{self.n_hour} hour median')
            ax[1].plot(dusk_equ_resampled, color = 'tab:red', label = f'{self.n_hour} hour median')
                
            for i in range(len(ax)):
                ax[i].set_ylabel('Ion Mass [u]')
                ax[i].legend(loc = 'lower right')
                ax[i].axhline(y = 16, color = 'black', ls = '--',linewidth=1)
                ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4)) 
                ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)

            ax[0].set_ylim(0, 30)
            ax[1].set_ylim(0,30 )
            ax[0].set_title('Equatorial dawnside')
            ax[1].set_title('Equatorial duskside')
        else:
            #Get the extracted dataframes
            ngt_equ, day_equ = self.extract_data(df, return_mean=True)
            # Resample by n hours median
            ngt_equ_resampled = ngt_equ['M_i_eff'].resample(f'{self.n_hour}H').median()
            day_equ_resampled = day_equ['M_i_eff'].resample(f'{self.n_hour}H').median()

            
            # Getting the MLT of the orbit
            mean = []  
            mean.append(round(ngt_equ["MLT"].mean()))
            mean.append(round(day_equ["MLT"].mean()))

            print('Plotting data:\n')
            fig, ax = plt.subplots(2,1,sharex=True)

            ax[0].scatter(ngt_equ.index, ngt_equ['M_i_eff'], s= 0.2, marker = '.')
            ax[1].scatter(day_equ.index, day_equ['M_i_eff'], s= 0.2, marker = '.',color = 'tab:orange')
            #Plotting the daily median 
            # df.groupby(ngt_equ.index.dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[0])
            # df.groupby(day_equ.index.dt.date)["M_i_eff"].median().plot(kind="line", color = 'tab:red', label = 'Daily median', ax=ax[1])
            ax[0].plot(ngt_equ_resampled, color = 'tab:red', label = f'{self.n_hour} hour median')
            ax[1].plot(day_equ_resampled, color = 'tab:red', label = f'{self.n_hour} hour median')


            for i in range(len(ax)):
                ax[i].set_ylabel('Ion Mass [u]')
                ax[i].legend(loc = 'lower right')
                ax[i].axhline(y = 16, color = 'black', ls = '--',linewidth=1)
                ax[i].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
                ax[i].text(.01, .99, f'MLT: {mean[i]}',ha='left', va='top', transform=ax[i].transAxes)

                    
            ax[0].set_ylim(0,30)
            ax[1].set_ylim(0,30)
            ax[0].set_title('Equatorial nightside')
            ax[1].set_title('Equatorial dayside')
       
        plt.gcf().autofmt_xdate()
        fig.suptitle(f'Baseline plot {title}: Swarm {self.sat_name}')
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
    # Satellites
    sat_A       = 'all_data_sat_A'
    sat_B       = 'all_data_sat_B'
    sat_C       = 'all_data_sat_C'
    # Baseline data file names
    before_june_A       = 'Baseline_before_2015_06_sat_A'
    before_june_B       = 'Baseline_before_2015_06_sat_B'
    before_june_C       = 'Baseline_before_2015_06_sat_C'
    before_december_A   = 'Baseline_before_2015_12_sat_A'
    before_december_B   = 'Baseline_before_2015_12_sat_B'
    before_december_C   = 'Baseline_before_2015_12_sat_C'
    before_september_A  = 'Baseline_before_2017_09_sat_A'
    before_september_B  = 'Baseline_before_2017_09_sat_B'
    before_september_C  = 'Baseline_before_2017_09_sat_C'
    before_august_A     = 'Baseline_before_2018_08_sat_A'
    before_august_B     = 'Baseline_before_2018_08_sat_B'
    before_august_C     = 'Baseline_before_2018_08_sat_C'

    after_june_A        = 'Baseline_after_2015_06_sat_A'
    after_june_B        = 'Baseline_after_2015_06_sat_B'
    after_june_C        = 'Baseline_after_2015_06_sat_C'
    after_december_A    = 'Baseline_after_2015_12_sat_A'
    after_december_B    = 'Baseline_after_2015_12_sat_B'
    after_december_C    = 'Baseline_after_2015_12_sat_C'
    after_september_A   = 'Baseline_after_2017_09_sat_A'
    after_september_B   = 'Baseline_after_2017_09_sat_B'
    after_september_C   = 'Baseline_after_2017_09_sat_C'
    after_august_A      = 'Baseline_after_2018_08_sat_A'
    after_august_B      = 'Baseline_after_2018_08_sat_B'
    after_august_C      = 'Baseline_after_2018_08_sat_C'


    start_time      = time.time()
    #Creating objects for the June 2015 storm
    june_storm_A    = plotting(dir+june_A)
    june_storm_B    = plotting(dir+june_B)
    june_storm_C    = plotting(dir+june_C)
    june_storm_A.plot_june_storm()
    june_storm_B.plot_june_storm()
    june_storm_C.plot_june_storm()

    #Creating objects for the December 2015 storm
    december_storm_A    = plotting(dir+december_A)
    december_storm_B    = plotting(dir+december_B)
    december_storm_C    = plotting(dir+december_C)
    december_storm_A.plot_december_storm(dawn_dusk=True)
    december_storm_B.plot_december_storm()
    december_storm_C.plot_december_storm(dawn_dusk=True)

    #Creating objects for the September 2017 storm
    september_storm_A    = plotting(dir+september_A)
    september_storm_B    = plotting(dir+september_B)
    september_storm_C    = plotting(dir+september_C)
    september_storm_A.plot_september_storm()
    september_storm_B.plot_september_storm()
    september_storm_C.plot_september_storm()

    #Creating objects for the August 2018 storm
    august_storm_A    = plotting(dir+august_A)
    august_storm_B    = plotting(dir+august_B)
    august_storm_C    = plotting(dir+august_C)
    august_storm_A.plot_august_storm()
    august_storm_B.plot_august_storm()
    august_storm_C.plot_august_storm()

    #Plotting baseline or not
    baseline_plot = False

    if baseline_plot:
        var_list = [before_june_A,before_june_B,before_june_C,before_december_A,before_december_B,
                    before_december_C,before_september_A,before_september_B,before_september_C,
                    before_august_A,before_august_B,before_august_C,after_june_A,after_june_B,
                    after_june_C,after_december_A,after_december_B,after_december_C,after_september_A,
                    after_september_B,after_september_C,after_august_A,after_august_B,after_august_C]
        titles  = ['before June 2015 storm',    'before June 2015 storm',       'before June 2015 storm',
                'before December 2015 storm','before December 2015 storm',   'before December 2015 storm',
                'before September 2017 storm','before September 2017 storm', 'before September 2017 storm',
                'before August 2018 storm',  'before August 2018 storm',     'before August 2018 storm',
                'after June 2015 storm',     'after June 2015 storm',        'after June 2015 storm',
                'after December 2015 storm', 'after December 2015 storm',    'after December 2015 storm',
                'after September 2017 storm','after September 2017 storm',   'after September 2017 storm',
                'after August 2018 storm',   'after August 2018 storm',      'after August 2018 storm']
        
        for i, element in enumerate(var_list):
            storm = plotting(dir+element)
            if (element in [before_december_A, before_december_C, after_december_A, after_december_C, before_september_B]): 
                storm.plot_baseline(dawn_dusk=True, title=titles[i])
            else:
                storm.plot_baseline(title=titles[i])
        
    

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



