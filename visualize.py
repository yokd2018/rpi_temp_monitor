#!/usr/bin/python
#coding: utf-8

import os
import sys
import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.finance as mpl_finance
import matplotlib.dates as mdates

from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO

from uploader import upload_to_google_drive

import configuration as CONF

log_dir = CONF.log_dir

dt_fmt_date = '%Y-%m-%d'
dt_fmt_time = '%Y-%m-%d %H:%M:%S'
log_level=DEBUG
log_formatter = Formatter('%(asctime)s %(levelno)s %(funcName)s:%(lineno)d %(message)s')

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(log_level)
handler.setFormatter(log_formatter)
logger.setLevel(log_level)
logger.addHandler(handler)
logger.propagate = False

def get_plot_data(key, dt):
    d = dt.strftime(dt_fmt_date)
    csv_file = os.path.join(log_dir,
                   '-'.join(['temperature', key, d]))
    f = open(csv_file, "r")
    lines = f.readlines()
    data = [ l.split(',') for l in lines ]
    return data

def plot(data_raw, title, filename):

    # openとcloseは温度計測インターバルで表示が崩れるので使わない。
    # open == closeとし、平均値を表示する。
    data = [ [mdates.date2num(datetime.datetime.strptime(j[0],dt_fmt_time)), 
                 float(j[1]), float(j[1]), float(j[2]), float(j[3])]
                 for j in data_raw ]

    fig = plt.figure(figsize=(12, 4))
    ax = fig.add_subplot(1, 1, 1)
    ax.set_ymargin(0.001)
    mpl_finance.candlestick(ax, data, width=0.005, alpha=0.5, colorup='r', colordown='b')
    
    ax.grid()
    locator = mdates.AutoDateLocator()
    formatter = mdates.AutoDateFormatter(locator)
    formatter.scaled[1.0/24] = '%H:%M'
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.set_title(title)
    plt.savefig(filename)

import pdb
if __name__ == '__main__':
    tgt_day = []
    if len(sys.argv) > 1:
        tgt_day.append(datetime.datetime.strptime(sys.argv[1],dt_fmt_date))
    else:
        now = datetime.datetime.now()
        td_1d = datetime.timedelta(days=1)
        tgt_day.append(now)
        tgt_day.append(now - td_1d)

    for dt in tgt_day:
        for key in 'cpu', 'disk':
            data = get_plot_data(key, dt)

            dt = datetime.datetime.strptime(data[0][0],dt_fmt_time)
            d = dt.strftime(dt_fmt_date)

            title = "Temperature(%s): %s" % (key, d)
            pngfile = os.path.join(log_dir, "temperature-%s-%s.png" % (key, d))
            csvfile = os.path.join(log_dir, "temperature-%s-%s" % (key, d))

            plot(data, title, pngfile)
            upload_to_google_drive(pngfile, CONF.gd_image_folder)
            upload_to_google_drive(csvfile, CONF.gd_csv_folder)






