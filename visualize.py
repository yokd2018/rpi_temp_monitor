#!/usr/bin/python
#coding: utf-8

import os
import sys
from datetime import timedelta
from datetime import datetime as dt

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.finance as mpl_finance
import matplotlib.dates as mdates

import ConfigParser
inifile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rpi_temp_monitor.ini")
inifile = ConfigParser.SafeConfigParser()
inifile.read(inifile_path)

log_dir = inifile.get("dirs", "log_dir")

dt_fmt_date = '%Y-%m-%d'
dt_fmt_time = '%Y-%m-%d %H:%M:%S'

def get_plot_data(key, day):
    '''
    過去のデータから、日付とkeyをもとに
    plotするデータを抽出
    '''
    d = day.strftime(dt_fmt_date)
    csv = os.path.join(log_dir, "temperature-%s-%s.csv" % (key, d))

    try:
        with open(csv, "r") as f:
            lines = f.readlines()
            data = [ l.split(',') for l in lines ]
    except IOError as e:
        print "IOError in get_plot_data"
        print e
        data = [] 

    return data

def plot(key, day, title, filepath, inc24h=False):

    data_raw = get_plot_data(key, day)

    if inc24h:
        if len(data_raw) > 0:
            latest = dt.strptime(data_raw[-1][0], dt_fmt_time)
        else:
            latest = day
        bef24h = latest - timedelta(days=1)
        daya_yest = [ l for l in get_plot_data(key, bef24h) if
                     dt.strptime(l[0], dt_fmt_time) > bef24h ]
        data_raw = daya_yest + data_raw

    # openとcloseは温度計測インターバルで表示が崩れるので使わない。
    # open == closeとし、平均値を表示する。
    data = [ [mdates.date2num(dt.strptime(j[0],dt_fmt_time)), 
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
    plt.savefig(filepath)

if __name__ == '__main__':
    now = dt.now()
    yest = now - timedelta(days=1)

    plot('cpu', now, "test1", os.path.join(log_dir, "test1.png"), inc24h=True)
    plot('cpu', yest, "test2", os.path.join(log_dir, "test2.png"))
