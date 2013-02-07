# -*- coding: utf-8 -*-
"""
author: James Morrison
"""
import unittest
import os
import raw_combined
import pandas as pd
import wave_stats

print os.getcwd()
wave_height_dataframe = pd.load('wave_height_dataframe')
#zero_crossing_df = pd.load('zero_crossing_dataframe')
    
# class Test_Load_Raw_Files(unittest.TestCase):

    # def setUp(self):
        # try:        
            # folder_path = 'buoy_data'
            # raw_combined.Load_Raw_Files(folder_path,2005)
        # except WindowsError:
            # print "Load Raw Files failed"

    # def test_wave_height_dataframe(self):
        # wave_height_dataframe = pd.load('wave_height_dataframe')
        # self.assertEqual(len(wave_height_dataframe),319118)

class Test_Wave_Stats(unittest.TestCase):

    def setUp(self):
        #Test
        print("Test")

    def test_wave_height_dataframe(self):
        raw_plus_std = pd.load('buoy_data\\2005\\July\\raw_plus_std')
        wave_stats.Wave_Stats(raw_plus_std)
        wave_height_dataframe = pd.load('wave_height_dataframe')
        self.assertEqual(len(wave_height_dataframe),318125)
        
if __name__=='__main__':
    unittest.main()    
        