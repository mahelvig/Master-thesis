import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import time
import matplotlib.ticker as ticker
import seaborn
from read_feather import data

def read_file(dir):
    #Function that takes a file (here/is/my/file_name) and returna a data frame
    df = data.read_feather(dir,dir)
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


    return df, sign_index_list


def box_plot(df,start_date,end_date,sign_index_list):
    lst=[]
    # df.groupby(df['Timestamp'].dt.date)['M_i_eff'].boxplot(subplots=False, figsize=(12,9), rot=90)
    # lst.append(x)
    # print(lst)
    
    # # # df.(column = 'M_i_eff',by='Orbit_number')
    # # df.groupby(df['Timestamp'].dt.date)["M_i_eff"].median().plot(kind="line",rot=45)
    
    # df.groupby('Orbit_number')['M_i_eff'].plot(color='b')
    # plt.ylim(0,30)
    # plt.show()
    df2 = df[['Timestamp','Orbit_number', 'M_i_eff',]].copy()
    df2['Timestamp'] = pd.to_datetime(df2['Timestamp'])

    df2.set_index(df2['Timestamp'], inplace = True)
    x = df2.groupby('Orbit_number')['M_i_eff'].median()
    



    fig, ax = plt.subplots()
    # seaborn.boxplot(data=df2,
    # x = 'Orbit_number',#df2[start_date:end_date].index.dayofyear,
    # y = 'M_i_eff',#df2[start_date:end_date]['M_i_eff'], 
    # color='tab:blue',
    # ax = ax)

    # ax.set_xticks(sign_index_list)
    # df2[sign_index_list].index.strftime('%Y-%m-%d'),
    # q = ax.set_xticklabels(labels = df2['Orbit_number'].unique(),
    # rotation=45, ha='right')
    # label2 = 1
    # for index, label in enumerate(ax.set_xticklabels(q)):
    #     if label == label2:
    #         label.set_visible(False)
    #     label2 = label
    plt.plot(df2['Timestamp'][sign_index_list][:-1],x, color = 'red')
    plt.axhline(y=16)
    plt.gcf().autofmt_xdate()

    ax.set_ylim(0,30)
    

    



if __name__ == '__main__':
    dir         = 'storm_data/Storms/'
    #The chosen satellite and date to evaluate
    sat_name    = ['A','B','C']
    start_year  = [2015,    2015,   2017,   2018,   2017]
    start_month = [6,       12,     9,      8,      3   ] 
    start_day   = [15,      17,     4,      20,     14  ]

    end_year    = [2015,    2015,   2017,   2018,   2017]
    end_month   = [6,       12,     9,      8,      3   ]
    end_day     = [30,      28,     15,     31,     20  ]

    for i, sat in enumerate(sat_name):
        for j in range(len(start_year)):

            dir2 = f'{str(start_year[j])}_{"0" if start_month[j] <10 else ""}{start_month[j]}_sat_{sat}'
            
            df = read_file(dir+dir2)
            df, sign_index_list = orbit_cutter(df)
            start_date  = f'{str(start_year[j])}-{"0" if start_month[j] <10 else ""}{start_month[j]}-{"0" if start_day[j] <10 else ""}{start_day[j]}'
            end_date  = f'{str(end_year[j])}-{"0" if end_month[j] <10 else ""}{end_month[j]}-{"0" if end_day[j] <10 else ""}{end_day[j]}'
            box_plot(df,start_date,end_date, sign_index_list)
            plt.title(f'Boxplot_{dir2}')
            plt.savefig(f'storm_data/Plots/Boxplot_{dir2}.png')
