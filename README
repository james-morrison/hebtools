This project has a number of Python files for processing raw Datawell Waverider
files into a more managable time series. The main module is 'raw_combined' 
described below, this project allows easier calculation of statistics from the
displacment data, and more sophisticated masking of improbable data than
is available from existing software packages.

Given the path of a Datawell Waverider buoy data directory containing year 
subfolders, the 'raw_combined' module will then process the records from the 
raw files into a pandas DataFrame with columns 'sig_qual', 'heave', 'north' 
and 'west' the index is a DateTimeIndex.  

The 'raw_combined' module has a class Load_Raw_Files which can iterate 
through the years, then months folders in the supplied buoy directory, 
saving pandas DataFrames in each month directory.  

The code skips empty or erroneously long files and each record is rounded to 
the nearest then rounded to the nearest tenth of a second, so the sequence is 
slightly irregular. Caution should be taken in treating the timestamps as 
absolute values, they are a best approximation in the context of the time 
series. The first value in every raw file is treated as the very start of that
half hour period, e.g. for the file Buoy_Name}2011-12-05T18h30Z.raw  the first
record will have a timestamp of 18:30:00 ( Hours:Minutes:Seconds ).  

Peak and troughs are detected for the heave values in the 'extrema' module then
masking is applied to data that has quality issues in the *error_check* module. 
In the *wave_stats* module wave heights and zero crossing periods are 
calculated, wave heights are calculated from peak to trough.

'problem_file_concat' module produces a csv file with the filenames of all
raw files that could not be processed, this module can be run after 
'raw_combined'.

'wave_concat' module can be run after 'raw_combined' to create a complete
dataframe of all wave heights timestamped and sorted temporally for each buoy.
Statistics are then generated on wave sets derived from the complete dataframe 
which are then exported as an Excel workbook ( .xlsx file ). This module 
requires a directory path that contains buoy directories and their names, the 
set size used for statistic calculation can be by number of waves or time 
interval.

'wad_to_dataframe' is a module than can process a Nortek AWAC wad file. The
pressure column can be then be processed in the same way as the Waverider heave
displacement without the error correction.

'test_raw_combined' is a module for testing the Load_Raw_Files class, example
buoy data is required to test. 

Requires: 
Numpy ( numpy.scipy.org )
Pandas ( pandas.pydata.org )
Matplotlib ( matplotlib.org )
openpyxl ( bitbucket.org/ericgazoni/openpyxl/src )

Almost all of the above requirements can be satisfied with a Python 
distribution like Anaconda CE from http://continuum.io/downloads.html
openpyxl can be installed afterwards by running 'easy_install openpyxl' from 
the Anaconda scripts directory.