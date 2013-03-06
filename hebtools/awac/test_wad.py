# -*- coding: utf-8 -*-
"""
author: James Morrison
"""
import unittest
import os
import pandas as pd
from hebtools.awac import parse_wad

class TestParseWad(unittest.TestCase):

    number_of_records = 100000

    def setUp(self):
        try:        
            parse_wad.ParseWad('../../awac_data/test_data.wad')
        except WindowsError:
            print "Load Wad Files failed"

    def test_wad_dataframe(self):
        wad_dataframe = pd.load('wad_dataframe')
        self.assertEqual(len(wad_dataframe),number_of_records)
        
if __name__=='__main__':
    unittest.main()   