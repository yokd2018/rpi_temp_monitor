#!/usr/bin/python

import sys
import pickle
import datetime
import subprocess
import os
from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO
import configuration as CONF

pklfile = CONF.pklfile
sys_thermal_file = '/sys/class/thermal/thermal_zone0/temp'
smart_cmd = 'smartctl -A /dev/sda'
dt_fmt_time = '%Y-%m-%d %H:%M:%S'
log_level=INFO
log_formatter = Formatter('%(asctime)s %(levelno)s %(funcName)s:%(lineno)d %(message)s')
aggregate_repeat=5

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(log_level)
handler.setFormatter(log_formatter)
logger.setLevel(log_level)
logger.addHandler(handler)
logger.propagate = False

def save_pkl(data):
    with open(pklfile, 'wb') as f:
        pickle.dump(data, f)

def load_pkl():
    try:
        with open(pklfile, 'rb') as f:
            data = pickle.load(f)

    except:
        logger.warn('pickle file not found')
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

if __name__ == '__main__':

    data = load_pkl()
    now = datetime.datetime.now()
    sample = SampleData(now)

    cpu_temp = get_cpu_temp()
    sample.add_data('cpu', cpu_temp)

    disk_temp = get_disk_temp()
    sample.add_data('disk',  disk_temp)

    data.append(sample)
    save_pkl(data)

    logger.debug('appended sample: %s, %s, %s', 
                   sample.get_time_str(), cpu_temp, disk_temp)

    if len(data) >= aggregate_repeat:
        for key in 'cpu', 'disk':
            agg_text = data_aggregation(data, key)
            d = agg_text.split()[0]
            out_file = os.path.join(CONF.log_dir,
                           '-'.join(['temperature', key, d]))
            write_data(out_file, agg_text)
            logger.debug('aggregate: %s', agg_text)
        data = []
        save_pkl(data)


