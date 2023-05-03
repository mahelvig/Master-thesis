import numpy as np 

import matplotlib.pyplot as plt 

import datetime as dt
import pandas as pd
import apexpy
from time import sleep
from tqdm import tqdm, trange  
data_list = ['Longitude', 'Timestamp', 'Latitude']
sat_list = ['A']

path = 'D:/VSCode/'

# for sat in sat_list:
#     for name in data_list:
#         exec(f'{name} = np.load("{path}Data_{sat}_{name}.npy", allow_pickle = True)')

dir = 'master/storm_data/Storms/all_data_sat_A'
df = pd.read_feather(dir)

print(df)


# a = np.zeros(len(Timestamp))

# print(f'### Generating MLT data for satellite {sat} ###')
# for i in trange(len(Timestamp)): 

#     apex_out = apexpy.Apex(Timestamp[i])
#     atime = pd.to_datetime(Timestamp[i])
#     mlat, mlt = apex_out.convert(Latitude[i], Longitude[i], 'geo', 'mlt', datetime=atime)
#     a[i] = mlt
    
# print(a)
# print(f'### Currently saving the data for satellite {sat} ###')
# np.save('D:/VSCode/Data_A_MLT', a)