hebtools 

This python package processes raw Datawell Waverider files into a flexible time 
series. The code allows easier calculation of statistics from the displacment 
data, more sophisticated masking of improbable data and the ability to deal with 
larger timeseries than is available from existing software. Similar code is also 
used to process pressure data from Nortek AWAC sensors details are described 
below. 

The code is organised into one main package named hebtools with three 
subpackages awac, dwr and common. common for modules used by the other 
subpackages. 

dwr 

In the case of a Datawell Waverider buoy the buoy data directory containing year 
subfolders must be passed to the load method of the parse_raw module which then 
iterates through the years. To call the module you can use the code below: 

from hebtools.dwr import parse_raw parse_raw("path_to_buoy_data") 

The module then processes the records from the raw files into a pandas DataFrame 
a good format for doing time series analysis. As well as the large DataFrame 
raw_plus_std command will also create a smaller wave_height_dataframe providing 
details on individual waves extracted from the displacements. An optional year 
parameter can be supplied to process a specific year folder. For more details on 
the approach taken to process the files please see the wiki 

Masking and calculation of the standard deviation of displacement values takes 
place in the error_check module 

problem_file_concat module produces a csv file with the filenames of all raw 
files that could not be processed, this module can be run after parse_raw. 

common 

Peak and troughs are detected for the heave/pressure values in the GetExtrema 
class. In the WaveStats class wave heights and zero crossing periods are 
calculated, wave heights are calculated from peak to trough. 

awac 

In the awac folder there is a ParseWad class that can process a Nortek AWAC wad 
file. The pressure column can be then be processed in the same way as the 
Waverider heave displacement without the error correction. There is an 
awac_stats.py module which uses an approach similar to wave_concat for 
calculating time interval based statistics. parse_wap module takes a Nortek wave 
parameter file and generates a time indexed pandas Dataframe. 

Testing 

The test_dwr module for testing the parse_raw module and WaveStats class, 
example buoy data is required to test, 1 month of anonymised data is provided in 
buoy_data.zip. test_awac module tests the parse_wad and parse_wap modules. Short 
anonymised test data sets for wap and wad files are in the awac_data folder. 

Statistic outputs 

The dwr/wave_concat module can be run after parse_raw to create a complete 
dataframe of all wave heights timestamped and sorted temporally for each buoy. 
This uses data from the monthly wave_height_dataframe files, statistics are then 
calculated on the wave sets and then exported as an Excel workbook ( .xlsx file 
). This module needs to be passed a path to a buoy data directory, the set size 
used for statistic calculation are the raw file names. 

The project was developed with data received from Waverider MKII and MKIII buoys 
with RFBuoy v2.1.27 producing the raw files. The AWAC was a 1MHz device and 
Storm v1.14 produced the wad files. The code was developed with the assistance 
of the Hebridean Marine Energy Futures project. 

Requires: 

- Python 2.7 ( developed and tested with 2.7.3 ) 
- numpy ( developed and tested with 1.6.2 ) 
- pandas ( minimum 0.10.1 ) 
- matplotlib ( developed and tested with 1.2.0 ) 
- openpyxl ( developed and tested with 1.6.1 ) 

Almost all of the above requirements can be satisfied with a Python distribution 
like Anaconda CE. 

openpyxl can be installed afterwards by running 'easy_install openpyxl' from the 
Anaconda scripts directory. 

Recommended optional dependencies for speed are numexpr and bottleneck, Windows 
binaries for these packages are available from Christoph Gohlke's page 

