# -*- coding: utf-8 -*-
"""
author: James Morrison
"""
import unittest
import os
import raw_combined
import pandas as pd

print os.getcwd()
wave_height_dataframe = pd.load('wave_height_dataframe')
#zero_crossing_df = pd.load('zero_crossing_dataframe')
    
class Test_DataFrames(unittest.TestCase):

    def setUp(self):
        try:        
            folder_path = 'D:\New_Datawell\\buoy_data'
            raw_combined.Load_Raw_Files(folder_path,2005)
        except WindowsError:
            print "Load Raw Files failed"

    def test_wave_height_dataframe(self):
        wave_height_dataframe = pd.load('wave_height_dataframe')
        self.assertEqual(len(wave_height_dataframe),319118)
        
if __name__=='__main__':
    unittest.main()    
        