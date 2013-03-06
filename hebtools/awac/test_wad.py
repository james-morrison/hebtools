# -*- coding: utf-8 -*-
"""
author: James Morrison
"""
import unittest
import os
import pandas as pd
from hebtools.awac import parse_wad

number_of_records = 998

class TestParseWad(unittest.TestCase):

    def setUp(self):
        try:        
            parse_wad.ParseWad('../../awac_data/test_data.wad')
        except WindowsError:
            print "Load Wad Files failed"

    def test_wad_dataframe(self):
        wad_dataframe = pd.load('test_data_wad_df')
        self.assertEqual(len(wad_dataframe),number_of_records)
        
if __name__=='__main__':
    unittest.main()   