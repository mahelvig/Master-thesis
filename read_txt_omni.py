import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as ticker
### This file creates the omni data plots used in the thesis ###

def readfile(file_name):
    ###Function that reads the file and creates a dataframe###
    headers = ['EPOCH_TIME', 'MAG_AVG_B-VECTOR', 'BZ,_GSE', 'FLOW_PRESSURE','DST']
    dtypes = {'MAG_AVG_B-VECTOR': 'float', 'BZ,_GSE': 'float', 'FLOW_PRESSURE': 'float','DST':'float'}
    parse_dates = ['EPOCH_TIME']
    df2     = pd.read_csv(file_name, delimiter='\s\s\s+', comment = '#', index_col='EPOCH_TIME',
                            parse_dates=parse_dates, dayfirst = True, dtype=dtypes, engine='python',
                            skipinitialspace= True)
    print(file_name)
    #Remove values set to default value
    condition1 = (df2['MAG_AVG_B-VECTOR']!=9999.99)
    condition2 = (df2['BZ,_GSE']!=9999.99)
    condition3 = (df2['FLOW_PRESSURE']!=99.9900)
    df          = df2.where(condition1&condition2&condition3)

    # print(df) #Uncomment if you want to print the dataframe
    return df, df2


def plot2(file_name,title):
    df,df2 = readfile(file_name)

    params = {'legend.fontsize': 'x-large',
          'figure.figsize': (10, 5),
         'axes.labelsize': 'medium',
         'axes.titlesize':'small',
         'xtick.labelsize':'small',
         'ytick.labelsize':'small'}
    plt.rcParams.update(params)

    font_size = 10

    fig, ax = plt.subplots(4,1,sharex=True)
    ax[0].set_ylabel('Total IMF strength \n[nT]',fontsize=font_size)
    ax[1].set_ylabel('IMF '+ r'$B_z$'+'\n[nT]',fontsize=font_size)
    ax[1].axhline(y = 0, color = 'black', ls='--',linewidth=1)
    ax[2].set_ylabel('Flow Pressure \n[nPa]',fontsize=font_size)
    ax[3].set_ylabel('Dst-index \n[nT]',fontsize=font_size)
    ax[3].axhline(y = 0, color = 'black', ls='--',linewidth=1)
    
    ax[0].plot(df.index, df['MAG_AVG_B-VECTOR'])
    ax[1].plot(df.index, df['BZ,_GSE'])
    ax[2].plot(df.index, df['FLOW_PRESSURE'])
    # Using df2 as it has complete data for the Dst-index
    ax[3].plot(df2.index, df2['SYM/H_INDEX'])

    #Finding minimun value and the timestamp of Dst-index 
    min_value = df2['SYM/H_INDEX'].max()
    min_value = df['MAG_AVG_B-VECTOR'].max()
    min_idx = df2['SYM/H_INDEX'].idxmin()
    print('Time: ',min_idx, '\nValue:', min_value)

    # ax[3].annotate('Dst-minimum', xy=(min_idx, min_value), xytext=(min_idx- pd.Timedelta(days=2), min_value + 50),
    #         arrowprops=dict(facecolor='red', shrink=0.01))
    ax[3].text(.99, .01, f'Dst minimum: {min_idx}',ha='right', va='bottom', transform=ax[3].transAxes)

    ax[0].set_ylim(0,50)
    ax[1].set_ylim(-40,40)
    ax[2].set_ylim(0,60)
    ax[3].set_ylim(-210,90)

    ax[0].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
    ax[1].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
    ax[2].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
    ax[3].xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
    ax[0].yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    ax[1].yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    ax[2].yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
    ax[3].yaxis.set_minor_locator(ticker.AutoMinorLocator(4))

    fig.suptitle(f'Plot of solar wind data during {title} storm')
    plt.xlabel('Time [UT]',fontsize=font_size)
    plt.savefig(f'storm_data/omni_data/Plot of solar wind data during {title} storm.png')
    # plt.show()
    # plt.close()
    return min_idx

def calculate_energy(file_name,ax):
    df1,df0 = readfile(file_name)

    min_idx = df0['SYM/H_INDEX'].idxmin()

    start_timestamp = min_idx - pd.Timedelta(days=2)
    end_timestamp   = min_idx + pd.Timedelta(days=2)

    df2 = df0.loc[(df0.index >= start_timestamp) & (df0.index <= end_timestamp)]
    

    total_energy = 0
    l_0 = 7 * 6_378_137 

    df2['epsilon'] = 1E7* df2['FLOW_SPEED,_GSE']/1000 * \
                     (df2['MAG_AVG_B-VECTOR']/1e9)**2 * \
                     (np.sin( np.arctan(df2['BY,_GSE']/df2['BZ,_GSE']) /2))**4 * l_0**2

    # for i, element in enumerate(df2.index):
    #     v = df2.loc[element, 'FLOW_SPEED,_GSE']
    #     B = df2.loc[element, 'MAG_AVG_B-VECTOR']
    #     B_y = df2.loc[element, 'BY,_GSE']
    #     B_z = df2.loc[element, 'BZ,_GSE']
    #     if  (v != 99999.9) &    (B != 9999.99) & \
    #         (B_y != 9999.99) &  (B_z != 9999.99):
    #         theta = np.arctan(B_y/B_z)

    #         epsilon = 1E7 * v/1000 * (B/1e9)**2 * (np.sin(theta/2))**4 * l_0**2
    #         total_energy += epsilon
    #         print(f'{epsilon:10.2f}',end='\r')
    # print(f'Total energy is :{total_energy/1_000_000_000:.2f} GJ')

    df3 = df2[(df2['FLOW_SPEED,_GSE'] != 99999.9) & (df2['MAG_AVG_B-VECTOR'] != 9999.99) & \
                  (df2['BY,_GSE'] != 9999.99) &  (df2['BZ,_GSE']!= 9999.99)]

    ax.plot(df3.index, df3['epsilon'], color='tab:blue')
    ax.set_ylabel('Energy [W]', color='tab:blue')
    ax.set_xlabel('Time [UT]')
    ax_y2 = ax.twinx()
    ax_y2.plot(df3.index, df3['BZ,_GSE'], color='tab:red')
    ax_y2.set_ylabel(r'$B_Z$ [nT]', color='tab:red')

    print(f'Total energy is: {df3["epsilon"].sum():.2f} Joules')
    
         


if __name__ == '__main__':

    dir = 'storm_data/omni_data/'
    file_names = ['2015_June.txt','2015_December.txt','2017_September.txt','2018_August.txt']
    titles = ['June 2015','December 2015', 'September 2017', 'August 2018']

    for i, name in enumerate(file_names):
        
        plot2(file_name=dir+name, title=titles[i])
    plt.show()

    # fig, ax = plt.subplots(4,1)

    # for i, name in enumerate(file_names):

    #     calculate_energy(file_name=dir+name,ax=ax[i])
    # plt.show()
    

