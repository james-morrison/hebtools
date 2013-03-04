**hebtools**

This python package processes raw 
**[Datawell Waverider](http://www.datawell.nl)** files into a flexible time 
series. The code allows easier calculation of statistics from the displacment
data, more sophisticated masking of improbable data and the ability to deal
with larger timeseries than is available from existing software. Similar code
is also used to process pressure data from 
**[Nortek AWAC](http://www.nortek-as.com/en/products/wave-systems/awac)** 
sensors details are described below.

The code is organised into one main package named **hebtools** with three 
subpackages **awac**, **dwr** and **common**. **common** for modules used by 
the other subpackages.

**dwr**

In the case of a Datawell Waverider buoy the buoy data directory containing year 
subfolders must be passed to the load method of the **parse_raw** module which
then iterates through the years. 

from hebtools.dwr import parse_raw

Processing the records from the raw files 
into a pandas DataFrame for each month with columns 'sig_qual', 'heave', 
'north' and 'west' the index being a pandas DateTimeIndex. An optional year 
parameter can be supplied to process a specifc year folder.

The code skips empty or erroneously long files and each record is rounded to 
the nearest tenth of a second, so the sequence is slightly irregular. Caution 
should be taken in treating the timestamps as absolute values, they are a best 
approximation in the context of the time series. The first value in every raw 
file is treated as the very start of that half hour period, e.g. for the file 
*Buoy_Name}2011-12-05T18h30Z.raw*  the first record will have a timestamp of 
18:30:00 ( Hours:Minutes:Seconds ). 

Masking and calculation of the standard deviation of displacement values 
takes place in the **error_check** module

**common**

Peak and troughs are detected for the heave/pressure values in the 
**GetExtrema** class. In the **WaveStats** class wave heights and zero 
crossing periods are calculated, wave heights are calculated from peak to 
trough.

**awac**

In the **awac** folder there is a **ParseWad** class that can 
process a Nortek AWAC wad file. The pressure column can be then be processed 
in the same way as the Waverider heave displacement without the error 
correction. There is an **awac\_stats.py** module which uses an approach 
similar to **wave_concat.py** for calculating time interval based statistics.

*Testing*

The **test_dwr** module for testing the **parse_raw** module and 
**WaveStats** class, example buoy data is required to test, 1 month of 
anonymised data is provided in **buoy\_data.zip**

*Statistic outputs*

The **dwr/wave\_concat** module can be run after **parse_raw** to create a complete
dataframe of all wave heights timestamped and sorted temporally for each buoy.
Statistics are then calculated on wave sets derived from the complete 
dataframe which are then exported as an Excel workbook ( .xlsx file ). This 
module requires a directory path that contains a buoy data directoriy and 
their names, the set size used for statistic calculation can be by number of 
waves or time interval. Currently the statistics sets for the the buoy data is
done by raw file name. 

The **problem\_file\_concat** module produces a csv file with the filenames of 
all raw files that could not be processed, this module can be run after 
**parse_raw**.

The project was developed with data received from Waverider MKII and MKIII 
buoys with RFBuoy v2.1.27 producing the raw files. The AWAC was a 1MHz device
and Storm v1.14 produced the wad files. The code was developed with the 
assistance of the [Hebridean Marine Energy Futures](http://hebmarine.com) 
project.

Requires: 

- [Python 2.7](http://python.org/download/) ( developed and tested with 2.7.3 )
- [Numpy](http://numpy.scipy.org) ( developed and tested with 1.6.2 )
- [Pandas](http://pandas.pydata.org) ( minimum 0.10.1 )
- [Matplotlib](http://matplotlib.org) ( developed and tested with 1.2.0 )
- [openpyxl](http://bitbucket.org/ericgazoni/openpyxl/src) ( developed and tested with 1.6.1 )

Almost all of the above requirements can be satisfied with a Python 
distribution like [Anaconda CE](http://continuum.io/downloads.html).

openpyxl can be installed afterwards by running 'easy_install openpyxl' from 
the Anaconda scripts directory.