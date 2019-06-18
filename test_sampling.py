#!/usr/bin/python

import unittest
import sampling as s
import os
import stat
from datetime import datetime as dt
import ConfigParser

inifile = ConfigParser.SafeConfigParser()
inifile.read("rpi_temp_monitor.ini")

log_dir = inifile.get("dirs", "log_dir")

class test_sampling(unittest.TestCase):
    def test_save_load_pkl(self):
        if os.path.exists(s.pklfile):
            os.remove(s.pklfile)
        saved_data = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        s.save_pkl(saved_data)
        loaded_data = s.load_pkl()
        self.assertEqual(saved_data, loaded_data)
        os.remove(s.pklfile)

    def test_get_cpu_temp(self):
        d = s.get_cpu_temp()
        self.assertIsInstance(d, float)

    def test_get_disk_temp(self):
        d = s.get_disk_temp()
        self.assertIsInstance(d, float)

    def test_write_data(self):
        test_out = os.path.join(log_dir,'test.log')
        if os.path.exists(test_out):
            os.remove(test_out)
        saved_data = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        s.write_data(test_out, saved_data)
        with open(test_out, 'r') as f:
            loaded_data = f.read()
        self.assertEqual(saved_data+ '\n', loaded_data)

    def test_data_aggregation_cpu(self):

        test_data = []

        for i in range(10):
            d = s.SampleData(dt(2019, 5, 25, 0, 10 + i, 10, 2000))
            d.add_data('cpu', 0 + i)
            d.add_data('disk', 10 + i)
            test_data.append(d)
        agg = s.data_aggregation(test_data, 'cpu')
        time = dt(2019, 5, 25, 0, 10 , 10, 2000).strftime('%Y-%m-%d %H:%M:%S')
        
        answer = ','.join([time, '4.5', '9', '0'])
        self.assertEqual(answer, agg)

    def test_data_aggregation_disk(self):

        test_data = []

        for i in range(10):
            d = s.SampleData(dt(2019, 5, 25, 0, 10 + i, 10, 2000))
            d.add_data('cpu', 0 + i)
            d.add_data('disk', 10 + i)
            test_data.append(d)
        agg = s.data_aggregation(test_data, 'disk')
        time = dt(2019, 5, 25, 0, 10 , 10, 2000).strftime('%Y-%m-%d %H:%M:%S')

        answer = ','.join([time, '14.5', '19', '10'])
        self.assertEqual(answer, agg)

if __name__ == "__main__":
    unittest.main()

