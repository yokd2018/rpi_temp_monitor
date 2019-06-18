#!/usr/bin/python
# coding: utf-8

import sys
import pickle
import datetime
import subprocess
import os
from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO
import ConfigParser

inifile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rpi_temp_monitor.ini")
inifile = ConfigParser.SafeConfigParser()
inifile.read(inifile_path)

basedir = inifile.get("dirs", "basedir")
log_dir = inifile.get("dirs", "log_dir")

pklfile = os.path.join(basedir, 'data.pkl')
sys_thermal_file = '/sys/class/thermal/thermal_zone0/temp'
smart_cmd = 'smartctl -A /dev/sda'
dt_fmt_time = '%Y-%m-%d %H:%M:%S'
aggregate_repeat=10

def save_pkl(data):
    with open(pklfile, 'wb') as f:
        pickle.dump(data, f)

def load_pkl():
    try:
        with open(pklfile, 'rb') as f:
            data = pickle.load(f)

    except:
        data = []

    return data

def get_cpu_temp():

    with open(sys_thermal_file, 'r') as f:
        cpu_temp = int(f.readline()) / 1000.0

    return float(cpu_temp)

def get_disk_temp():

    smart_out = subprocess.check_output(smart_cmd.split())
    find_194 = lambda a,b: a if a.startswith('194') else b
    temp_cel = reduce(find_194, smart_out.split('\n'))
    if not temp_cel.startswith('194'):
        raise Exception('Could not find the entry 194')
    disk_temp = temp_cel.split()[3]


    return float(disk_temp)

def write_data(fpath, text):
    with open(fpath, 'a') as f:
        f.write(text+'\n')

class SampleData:
    def __init__(self, time):
        self.t = time
        self.data = {}

    def add_data(self, key, value):
        self.data[key] = value

    def get_time_str(self):
        return self.t.strftime(dt_fmt_time)

def data_aggregation(data, key):
    #_o= data[0].data[key]
    #_c= data[-1].data[key]
    _avg = 1.0 * sum([ i.data[key] for i in data ]) / len(data)
    _h = max([ i.data[key] for i in data ])
    _l = min([ i.data[key] for i in data ])

    _dt = data[0].get_time_str()

    return ','.join(str(i) for i in [_dt, _avg, _h, _l])

def get_current_temperature():

    now = datetime.datetime.now()
    sample = SampleData(now)

    cpu_temp = get_cpu_temp()
    sample.add_data('cpu', cpu_temp)

    disk_temp = get_disk_temp()
    sample.add_data('disk',  disk_temp)

    return sample

def main():

    data = load_pkl()
    sample = get_current_temperature()

    data.append(sample)
    save_pkl(data)

    if len(data) >= aggregate_repeat:
        for key in 'cpu', 'disk':
            agg_text = data_aggregation(data, key)
            d = agg_text.split()[0]
            out_file = os.path.join(log_dir, "temperature-%s-%s.csv" % (key, d))
            write_data(out_file, agg_text)
        data = []
        save_pkl(data)

if __name__ == '__main__':
    main()

