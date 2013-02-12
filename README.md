The project processes raw **[Datawell Waverider](http://www.datawell.nl)** 
files into a flexible time series. The code allow easier calculation of 
statistics from the displacment data, more sophisticated masking of improbable
data and the ability to deal with larger timeseries than is available from 
existing software. The same code is also used to process pressure data from 
**[Nortek AWAC](http://www.nortek-as.com/en/products/wave-systems/awac)** 
sensors detailed below.

In the case of a Datawell Waverider buoy the data directory containing year 
subfolders must be supplied to the main **raw_combined.py** module. The class 
**Load\_Raw\_Files** then iterate through the years. Processing the records 
from the raw files into a pandas DataFrame for each month with columns 
'sig\_qual', 'heave', 'north' and 'west' the index being a pandas 
DateTimeIndex. An optional year parameter can be supplied to process a specifc
year folder.

The code skips empty or erroneously long files and each record is rounded to 
the nearest tenth of a second, so the sequence is slightly irregular. Caution 
should be taken in treating the timestamps as absolute values, they are a best 
approximation in the context of the time series. The first value in every raw 
file is treated as the very start of that half hour period, e.g. for the file 
*Buoy_Name}2011-12-05T18h30Z.raw*  the first record will have a timestamp of 
18:30:00 ( Hours:Minutes:Seconds ).  

Peak and troughs are detected for the heave values in the **extrema.py** module
then masking is applied to data that has quality issues in the 
**error_check.py** module. In the **wave\_stats.py** module wave heights and 
zero crossing periods are calculated, wave heights are calculated from peak to 
trough.

**problem\_file\_concat.py** module produces a csv file with the filenames of 
all raw files that could not be processed, this module can be run after 
**raw_combined.py**.

**wave\_concat.py** module can be run after **raw_combined.py** to create a 
complete dataframe of all wave heights timestamped and sorted temporally for 
each buoy. Statistics are then generated on wave sets derived from the complete
dataframe which are then exported as an Excel workbook ( .xlsx file ). This 
module requires a directory path that contains buoy directories and their 
names, the set size used for statistic calculation can be by number of waves or
time interval.

**wad\_to\_dataframe.py** is a module than can process a Nortek AWAC wad file. 
The pressure column can be then be processed in the same way as the Waverider 
heave displacement without the error correction.

**test\_raw\_combined.py** is a module for testing the Load\_Raw\_Files and 
Wave_Stats classes, example buoy data is required to test, 1 month of 
anonymised data is provided in **buoy\_data.zip**

The project was developed with data recieved from Waverider MKII and MKIII 
buoys with RFBuoy v2.1.27 producing the raw files. The AWAC was a 1MHz device
and Storm v1.14 produced the wad files. The code was developed with the 
assistance of the [Hebridean Marine Energy Futures](http://hebmarine.com) 
project.

Requires: 

- [Python 2.7](http://python.org/download/) ( developed and tested with 2.7.3 )
- [Numpy](http://numpy.scipy.org)
- [Pandas](http://pandas.pydata.org)
- [Matplotlib](http://matplotlib.org)
- [openpyxl](http://bitbucket.org/ericgazoni/openpyxl/src)

Almost all of the above requirements can be satisfied with a Python 
distribution like [Anaconda CE](http://continuum.io/downloads.html).

openpyxl can be installed afterwards by running 'easy_install openpyxl' from 
the Anaconda scripts directory.