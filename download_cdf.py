import wget
import pandas as pd
import os 
import zipfile


# Program that downloads SWARM data between a given start and end date
# and unzips the downloaded data to the correct directory

dir_name = 'storm_data/Downloads'

start_date  = "2016-11-16"
end_date    = "2016-11-17"
dates = pd.date_range(start_date,end_date)
sat_name = ['A','B','C']
for sat in sat_name:  
    for i in dates:
        year = str(i.date().year)
        month = str(i.date().month).zfill(2)
        day = str(i.date().day).zfill(2)

        file_name = f'SW_PREL_EFI{sat}IDM_2__{year}{month}{day}T000000_{year}{month}{day}T235959_0103.ZIP'
        if os.path.exists(dir_name+'/'+file_name):
            print(f'File already in {dir_name}')
        else:

            URL = f"https://swarm-diss.eo.esa.int/?do=download&file=swarm%2FAdvanced%2FPlasma_Data%2F2_Hz_Ion_Drift_Density_and_Effective_Mass_dataset%2FSat_{sat}%2FSW_PREL_EFI{sat}IDM_2__{year}{month}{day}T000000_{year}{month}{day}T235959_0103.ZIP"
            
            print(URL,end='\n')

            response = wget.download(URL,dir_name)


extension = ".ZIP"
for item in os.listdir(dir_name): # loop through items in dir
    if item.endswith(extension): # check for ".ZIP" extension
        file_name   = dir_name + "/" + item
        # Checks if file is already unzipped, unzips if not
        if os.path.exists('storm_data/all_data/'+ item[:-4]+'.cdf'):
            print(f'File is already unzipped to storm_data/all_data/')
        else:
            zip_ref     = zipfile.ZipFile(file_name) 
            zip_ref.extract(path='storm_data/all_data', member=item[:-4]+'.cdf') 
            zip_ref.close()
        # os.remove(file_name) # delete zipped filey
