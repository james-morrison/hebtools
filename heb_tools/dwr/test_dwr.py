# -*- coding: utf-8 -*-
"""
author: James Morrison
"""
import unittest
import os
import pandas as pd
from heb_tools.dwr import ParseRaw
from heb_tools.common import WaveStats

print os.getcwd()

number_of_waves = 313053
    
class TestParseRaw(unittest.TestCase):

   def setUp(self):
       #try:        
           folder_path = '../../buoy_data'
           parse_raw = ParseRaw()
           parse_raw.load(folder_path)
       #except WindowsError:
       #    print "Load Raw Files failed"

   def test_wave_height_dataframe(self):
       wave_height_dataframe = pd.load('wave_height_dataframe')
       self.assertEqual(len(wave_height_dataframe),number_of_waves)

# class Test_Wave_Stats(unittest.TestCase):

    # def setUp(self):
        # #Test
        # print("Test")

    # def test_wave_height_dataframe(self):
        # os.chdir(os.path.join('buoy_data','2005','july'))
        # raw_plus_std = pd.load('raw_plus_std')
        # wave_stats.Wave_Stats(raw_plus_std)
        # wave_height_dataframe = pd.load('wave_height_dataframe')
        # self.assertEqual(len(wave_height_dataframe),number_of_waves)
        
if __name__=='__main__':
    unittest.main()    
        