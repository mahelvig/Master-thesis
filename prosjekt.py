import matplotlib.pyplot as plt
import os
from read_cdf import read_cdf
import pandas as pd

### Program used to convert cdf-files to feather-files ###

class prosjekt:
    def __init__(self, input_list):
        #Save the wanted satellite globally
        self.sat_name   = input_list[0]

        #Save the wanted date globally
        self.start_year = str(input_list[1])
        self.start_month= str(input_list[2]).zfill(2)
        self.start_day  = str(input_list[3]).zfill(2)

        self.end_year = str(input_list[4])
        self.end_month= str(input_list[5]).zfill(2)
        self.end_day  = str(input_list[6]).zfill(2)

        #Main directory for SWARM data storage
        self.dir_main   = 'storm_data/all_data/'
    
    def path_check(self,dir:str):
        #Function that checks if file exists. 
        # Takes directory ('here/is/my/file_name.cdf') as argument and returns True or False
        return os.path.exists(dir)
    
    def name_file(self,sat_name:str, year:str, month:str, day:str):
        #Function that names the file we want to read.
        #Takes satellite name, year, month and day as arguments
        file_name = f'SW_PREL_EFI{sat_name}IDM_2__{year}{month}{day}T000000_{year}{month}{day}T235959_0103.cdf'
        return file_name


    def get_df(self, year:str, month:str, day:str):
        #Get dataframe of specified time frame,     
        #Takes year, month and day as arguments
   
        file_name = self.name_file(self.sat_name,year, month, day)
        # Check if file read exists
        file_exist = self.path_check(self.dir_main + file_name)
        
        if file_exist:
            print(f'### The file {file_name} exists. Making it a df ###')
            df = read_cdf(sat_name, year, month, day).read_file(self.dir_main, file_name)
            return df
        else:
            return print(f'### The file {file_name} does not exist ###')
        
    
    def combine_df(self):
        #Function that combines all the dfs into one
        #Create a list with all dates from the chosen start and end date
        start   = pd.to_datetime(f'{self.start_day}/{self.start_month}/{self.start_year}', dayfirst = True)
        end     = pd.to_datetime(f'{self.end_day}/{self.end_month}/{self.end_year}', dayfirst = True)
        dates   = pd.date_range(start=start, end=end)
        #Empty list for storing the extracted dataframes
        df_list = []
        #Loops through all the days 
        for i in dates:
            year    = str(i.date().year)
            month   = str(i.date().month).zfill(2)
            day     = str(i.date().day).zfill(2)
            df      = self.get_df(year, month, day)
            df_list.append(df)
        #Combine the dataframes for each day into one
        result  = pd.concat(df_list,ignore_index=True)
        #Prints the finished dataframe
        print("\n\nFinished combining all dataframes \nNow showing result:\n",result)
        #Saves it in the class and returns it
        self.df = result
        return result

        


if __name__ == '__main__':

    #The chosen satellite and date to evaluate
    sat_name    = ['A','B','C']
    start_year  = [2015,    2015,   2017,   2018,   2017]
    start_month = [6,       12,     9,      8,      3   ] 
    start_day   = [15,      17,     4,      20,     14  ]

    end_year    = [2015,    2015,   2017,   2018,   2017]
    end_month   = [6,       12,     9,      8,      3   ]
    end_day     = [30,      28,     15,     31,     20  ]

    start_year_baseline  = [2015,    2015,   2015,   2015,   2017,  2017,   2018,   2018]
    start_month_baseline = [6,       6,      12,     12,     8,     9,      8,      8   ] 
    start_day_baseline   = [12,      26,     12,     27,     30,    11,     15,     29  ]

    end_year_baseline    = [2015,    2015,   2015,   2016,   2017,  2017,   2018,   2018]
    end_month_baseline   = [6,       7,      12,     1,      9,     9,      8,      9   ]
    end_day_baseline     = [19,      2,      19,     2,      4,     18,     23,     6   ]
    
    baseline = False
    quiet_days = True

    if baseline:
        for i, sat in enumerate(sat_name):
            for j in range(len(start_year_baseline)):

                input_list   = [sat,start_year_baseline[j],start_month_baseline[j],start_day_baseline[j],end_year_baseline[j],end_month_baseline[j],end_day_baseline[j]]

                obj = prosjekt(input_list)
                df_finished = obj.combine_df()
                print('Dette er nummer:',j,"  before" if ((j+2)%2==0) else "  after")
                df_finished.to_feather(f'storm_data/Storms/Baseline_{"before" if ((j+2)%2==0) else "after"}_{str(start_year_baseline[j])}_{"0" if start_month_baseline[j] <10 else ""}{start_month_baseline[j]}_sat_{sat}')

    elif quiet_days:
         for i, sat in enumerate(sat_name):
            
            input_list   = [sat,2016,11,16,2016,11,17]
            obj = prosjekt(input_list)
            df_finished = obj.combine_df()
            df_finished.to_feather(f'storm_data/Storms/quiet_days_sat_{sat}')
            

    else:
        for i, sat in enumerate(sat_name):
            for j in range(len(start_year)):

                input_list   = [sat,start_year[j],start_month[j],start_day[j],end_year[j],end_month[j],end_day[j]]

                obj = prosjekt(input_list)
                df_finished = obj.combine_df()
                # df_finished.to_feather(f'master/storm_data/Storms/all_data_sat_{sat}')
                df_finished.to_feather(f'storm_data/Storms/{str(start_year[j])}_{"0" if start_month[j] <10 else ""}{start_month[j]}_sat_{sat}')

