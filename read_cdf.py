from spacepy import pycdf
import numpy as np
import pandas as pd

### Program used to read CDF-files. Mainly used through project.py ###

class read_cdf:
    #Class that reads data from a cdf-file and conert them to np.arrays
    #Takes the arguments sat_name('A','B' or 'C'), start_year(yyyy), start_month(1-12) and start_day(1-31)
    def __init__(self, sat_name:str, start_year:int, start_month:int, start_day:int):
        #Analysing and saving inputs
        self.sat_name    = sat_name   
        self.start_year  = start_year
        if type(start_month) != str:
            self.start_month = str(start_month).zfill(2)
        else:
            self.start_month = start_month
        if type(start_day) != str:
            self.start_day = str(start_day).zfill(2)
        else:
            self.start_day = start_day 
        
        #Directory
        self.dir = 'storm_data/all_data/'
        
    
    def read_file(self,dir:str, file_name):
        #Function that reads file and saves data
        #Takes the argument dir ('C:/Users/.../') and the file name
    
        cdf         = pycdf.CDF(dir+file_name)

        #Save the data a dataframe
        df = self.save_data(cdf)
        #Close the file
        cdf.close()
        #Save the data frame globally
        self.df = df

        return df

    def save_data(self, cdf):
        # cdf.keys()
        #Creates an empty dataframe
        df = pd.DataFrame()
        #Loops through the data and stores it in the dataframe
        for k in cdf:
            x   = cdf[k][...]
            #All multi dimentional arrays is kept out of the df
            if np.ndim(x) != 1:
                continue

            df[k] = x

        return df



if __name__ == '__main__':
    test = read_cdf('A',2015,6,22)
    test.read_file('C:/Users/Martin/OneDrive/03Python/master/storm_data/')
    print(test.df)