import pandas as pd
import numpy as np

class GetExtrema():

    def __init__(self, raw_displacements, column_name = 'heave'):    
        self.raw_displacements = raw_displacements
        self.get_peaks(column_name)
    
    def _datacheck_peakdetect(self, x_axis, y_axis):
        if x_axis is None:
            x_axis = list(range(len(y_axis)))
        
        if len(y_axis) != len(x_axis):
            raise ValueError
        
        #needs to be a numpy array
        y_axis = np.array(y_axis)
        x_axis = np.array(x_axis)
        return x_axis, y_axis
        
    def peakdetect(self, y_axis, x_axis = None, lookahead = 4, delta=0):
        """
        Converted from/based on a MATLAB script at: 
        http://billauer.co.il/peakdet.html
        
        function for detecting local maximas and minmias in a signal.
        Discovers peaks by searching for values which are surrounded by lower
        or larger values for maximas and minimas respectively
        
        keyword arguments:
        y_axis -- A list containg the signal over which to find peaks
        x_axis -- (optional) A x-axis whose values correspond to the y_axis list
            and is used in the return to specify the postion of the peaks. If
            omitted an index of the y_axis is used. (default: None)
        lookahead -- (optional) distance to look ahead from a peak candidate to
            determine if it is the actual peak (default: 200) 
            '(sample / period) / f' where '4 >= f >= 1.25' might be a good value
        delta -- (optional) this specifies a minimum difference between a peak and
            the following points, before a peak may be considered a peak. Useful
            to hinder the function from picking up false peaks towards to end of
            the signal. To work well delta should be set to delta >= RMSnoise * 5.
            (default: 0)
                delta function causes a 20% decrease in speed, when omitted
                Correctly used it can double the speed of the function
        
        return -- two lists [max_peaks, min_peaks] containing the positive and
            negative peaks respectively. Each cell of the lists contains a tupple
            of: (position, peak_value) 
            to get the average peak value do: np.mean(max_peaks, 0)[1] on the
            results to unpack one of the lists into x, y coordinates do: 
            x, y = zip(*tab)
        """
        max_peaks = []
        min_peaks = []
        dump = []   #Used to pop the first hit which almost always is false
           
        # check input data
        x_axis, y_axis = self._datacheck_peakdetect(x_axis, y_axis)
        # store data length for later use
        length = len(y_axis)
        
        
        #perform some checks
        if lookahead < 1:
            raise ValueError("Lookahead must be '1' or above in value")
        if not (np.isscalar(delta) and delta >= 0):
            raise ValueError("delta must be a positive number")
        
        #maxima and minima candidates are temporarily stored in
        #mx and mn respectively
        mn, mx = np.Inf, -np.Inf
        
        #Only detect peak if there is 'lookahead' amount of points after it
        for index, (x, y) in enumerate(list(zip(x_axis[:-lookahead], 
                                            y_axis[:-lookahead]))):
            if y > mx:
                mx = y
                mxpos = x
            if y < mn:
                mn = y
                mnpos = x
            
            ####look for max####
            try:
                if y < mx-delta and mx != np.Inf:
                    #Maxima peak candidate found
                    #look ahead in signal to ensure that this is a peak and not jitter
                    if y_axis[index:index+lookahead].max() < mx:
                        max_peaks.append([mxpos, mx])
                        dump.append(True)
                        #set algorithm to only find minima now
                        mx = np.Inf
                        mn = np.Inf
                        if index+lookahead >= length:
                            #end is within lookahead no more peaks can be found
                            break
                        continue
                    #else:  #slows shit down this does
                    #    mx = ahead
                    #    mxpos = x_axis[np.where(y_axis[index:index+lookahead]==mx)]
                
                ####look for min####
                if y > mn+delta and mn != -np.Inf:
                    #Minima peak candidate found 
                    #look ahead in signal to ensure that this is a peak and not jitter
                    if y_axis[index:index+lookahead].min() > mn:
                        min_peaks.append([mnpos, mn])
                        dump.append(False)
                        #set algorithm to only find maxima now
                        mn = -np.Inf
                        mx = -np.Inf
                        if index+lookahead >= length:
                            #end is within lookahead no more peaks can be found
                            break
                    #else:  #slows shit down this does
                    #    mn = ahead
                    #    mnpos = x_axis[np.where(y_axis[index:index+lookahead]==mn)]
        
            except TypeError:
                print(type(y), y)
                print(type(delta), delta)
                print(type(mx), mx)
                print(type(np.Inf), np.Inf)            
        #Remove the false hit on the first value of the y_axis
        try:
            if dump[0]:
                max_peaks.pop(0)
            else:
                min_peaks.pop(0)
            del dump
        except IndexError:
            #no peaks were found, should the function return empty lists?
            pass
            
        return [max_peaks, min_peaks]
    
    def get_extrema_timestamps(self, extrema, index):
        indexes = [x[0] for x in extrema]
        timestamps = [index[z] for z in indexes]
        return timestamps
    
    def get_extrema_df(self, extrema_index, index, extrema_type):
        extrema_timestamps = self.get_extrema_timestamps(extrema_index, index)
        return pd.DataFrame(np.ones(len(extrema_index), dtype=np.int64), 
                            columns = ['extrema'], 
                            index = extrema_timestamps)*extrema_type
    
    def get_peaks(self, column_name):
        print("start get_peaks")
        y = self.raw_displacements[column_name]
        index = self.raw_displacements.index
        _max, _min = self.peakdetect(y)
        maxima_df = self.get_extrema_df(_max, index, 1 )
        minima_df = self.get_extrema_df(_min, index, -1 )
        extrema_df = pd.concat([maxima_df, minima_df])
        extrema_df.save('extrema_df')
        raw_disp_with_extrema = self.raw_displacements.join(extrema_df)
        raw_disp_with_extrema = raw_disp_with_extrema.sort()
        self.raw_disp_with_extrema = raw_disp_with_extrema
