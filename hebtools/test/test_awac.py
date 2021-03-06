# -*- coding: utf-8 -*-
""" Module for testing awac package
@author: James Morrison
@license: MIT
"""
import unittest
import os
import pandas as pd
from hebtools.awac import parse_wad
from hebtools.awac import parse_wap
from hebtools.awac import awac_stats

awac_folder_path = os.path.abspath(os.path.join('data','awac')) + os.path.sep
print(awac_folder_path)
number_of_records = 999
wad_records = 99
number_of_awac_stats = 1

class TestAWAC(unittest.TestCase):

    def setUp(self):
        print("setUp")    

    def test_wad_dataframe(self):
        print("TestParseWad")
        try:        
            path = awac_folder_path + 'test_data.wad'
            parse_wad.ParseWad(path)
        except WindowsError:
            print("Load Wad Files failed")        
        wad_dataframe = pd.load('test_data_wad_df')
        self.assertEqual(len(wad_dataframe),number_of_records)
        


    def test_wap_dataframe(self):
        print("TestParseWap")
        try:        
            parse_wap.load(awac_folder_path + 'test_data.wap')
        except WindowsError:
            print("Load wap Files failed")
        wap_dataframe = pd.load('test_data_wap_df')
        self.assertEqual(len(wap_dataframe),wad_records)

    def test_awac_stats(self):
        print("TestAwacStats")
        try:
            path = awac_folder_path + 'test_data.wad'
            parse_wad.ParseWad(path)        
            awac_stats.process_wave_height(awac_folder_path + 'awac_wave_height_df')
        except WindowsError:
            print("Load wap Files failed")
        wave_height_dataframe = pd.load('awac_stats_30min')
        self.assertEqual(len(wave_height_dataframe),number_of_awac_stats)          
        
if __name__=='__main__':
    unittest.main()     