import pandas as pd
import numpy as np
import spacepy as sp
import matplotlib.pyplot as plt
from spacepy import pycdf
from tqdm import tqdm 
import time


dir = 'C:/Users/Martin/OneDrive/03Python/master/storm_data/'

cdf     = pycdf.CDF(dir + 'SW_PREL_EFIAIDM_2__20150621T000000_20150621T235959_0103.cdf')
cdf2    = pycdf.CDF(dir + 'SW_PREL_EFIAIDM_2__20150622T000000_20150622T235959_0103.cdf')
# cdf.readonly(False)
print(cdf['QDLatitude'][...],cdf['M_i_eff_Flags'][...])

print (cdf)

# cdf['mass'] =   cdf['QDLatitude'][:] > -50 and cdf['QDLatitude'][:]< 50 or \ cdf['QDLatitude'][:] > 130 and cdf['QDLatitude'][:]< 230

# df = cdf.where(cdf['QDLatitude'][:] > -50 and cdf['QDLatitude'][:]< 50)

# print(cdf)

liste = []
time_list = []
# for i, element in tqdm(enumerate(cdf['QDLatitude'][:])):
lengde = len(cdf['QDLatitude'][...])
i=0
for element in tqdm(cdf['QDLatitude'][...]):
    
    # if element > -50 and element < 50 or element > 130 and element < 230 :
    
    if element > -50 and element < 50:# or element > 130 and element < 230 :
        liste.append(cdf['M_i_eff_Flags'][i])
        time_list.append(cdf['Timestamp'][i])
    i+=1

# df = pd.DataFrame(cdf['QDLatitude'][:],  columns =['QDLatitude'])
# print(df)
# df2     = df.where(df['QDLatitude'] <-50 or df['QDLatitude'] > 50 , None)
# # print(df3)
# print(df2)


plt.figure(1)
# plt.plot(cdf['Timestamp'][:]    ,cdf['M_i_eff'][:])
# plt.plot(cdf2['Timestamp'][:]   ,cdf2['M_i_eff'][:])
plt.plot(time_list, liste)
plt.gcf().autofmt_xdate()
plt.ylim(0,25)

plt.figure(2)
plt.plot(cdf['Timestamp'][...]    ,cdf['QDLatitude'][...])
plt.plot(cdf2['Timestamp'][...]   ,cdf2['QDLatitude'][...])
plt.gcf().autofmt_xdate()

plt.show()

cdf.close()
cdf2.close()
print('The program has ended...')
