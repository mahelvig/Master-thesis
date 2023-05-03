import numpy as np

import matplotlib.pyplot as plt
import time
import datetime as dt
import pandas as pd
import apexpy
from time import sleep
from tqdm import tqdm, trange
data_list = ['Longitude', 'Timestamp', 'Latitude', 'Radius']
sat_list = ['C']

path = 'C:/Users/Martin/OneDrive/03Python/master/storm_data/Kristoffer/'

for sat in sat_list:
    for name in data_list:
        exec(f'{name} = np.load("{path}Data_{sat}_{name}.npy", allow_pickle = True)')

#KM
Radius = Radius/1000 - 6371

# print(Radius[0:10])
"""
Dette har jeg lyst til at fungerer______

Timestamp = Timestamp#x:x+100]
print(Timestamp)

Latitude = Latitude#x:x+100]
print(Latitude)

Longitude = Longitude#x:x+100]
print(Longitude)
Timestamp = Timestamp.astype('datetime64')
Timestamp = pd.to_datetime(Timestamp)
Timestamp = Timestamp.to_numpy()
"""
"""
# print('dette er:', Timestamp) #får følgende 'feil' her: COFRM:  DATE ******* is after the last recommended for extrapolation 1905.0
#kommer seg kun hit
atime = Timestamp
print('jeg kommer hit')
apex_out = apexpy.Apex(date = Timestamp)
print('Jeg kommer forbi første!!!')
mlat, mlt = apex_out.convert(Latitude, Longitude, 'geo', 'mlt', datetime=atime)
a = mlt
"""
n = 100000
x = 24292223- 20000*3
a = np.zeros(n)

# Dette fungerer opp til ett visst punkt___ (24650200 av 37 millioner)
#x = 0
print(f'### Generating MLT data for satellite {sat} ###')
for i in trange(len(Timestamp[x:x+n])):
    apex_out = apexpy.Apex(Timestamp[x+i])
    atime = pd.to_datetime(Timestamp[x+i])
    mlat, mlt = apex_out.convert(Latitude[x+i], Longitude[x+i], 'geo', 'mlt', datetime=atime, height = Radius[x+i])
    print(Timestamp[x+i],Latitude[x+i],Longitude[x+i], Radius[x+i])
   
    if np.isnan(mlt):
        print('Her feiler den:',x+i)
        print(Timestamp[x+i],Latitude[x+i],Longitude[x+i], Radius[x+i])
        # print('Her fungerer den:',x+i-1)
        # print(Timestamp[x+i-1],Latitude[x+i-1],Longitude[x+i-1], Radius[x+i-1])
        break
    a[i] = mlt


print(a)
print(f'### Currently saving the data for satellite {sat} ###')
# np.save('D:/VSCode/Data_B_MLT', a)