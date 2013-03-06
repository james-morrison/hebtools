# -*- coding: utf-8 -*-
"""
author: James Morrison
"""
import unittest
import os
import pandas as pd
from hebtools.awac import parse_wad
from hebtools.awac import parse_wap

number_of_records = 998
wad_records = 100

# class TestParseWad(unittest.TestCase):

    # def setUp(self):
        # try:        
            # parse_wad.ParseWad('../../awac_data/test_data.wad')
        # except WindowsError:
            # print "Load Wad Files failed"

    # def test_wad_dataframe(self):
        # wad_dataframe = pd.load('test_data_wad_df')
        # self.assertEqual(len(wad_dataframe),number_of_records)
        
class TestParseWap(unittest.TestCase):

    def setUp(self):
        try:        
            parse_wap.load('../../awac_data/test_data.wap')
        except WindowsError:
            print "Load Wad Files failed"

    def test_wap_dataframe(self):
        wap_dataframe = pd.load('test_data_wap_df')
        self.assertEqual(len(wap_dataframe),wad_records)        
        
if __name__=='__main__':
    unittest.main()   