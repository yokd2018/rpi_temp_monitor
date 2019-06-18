#!/usr/bin/python
# coding: utf-8

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os.path
import sys
import ConfigParser
from datetime import timedelta
from datetime import datetime as dt

import ConfigParser
inifile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rpi_temp_monitor.ini")
inifile = ConfigParser.SafeConfigParser()
inifile.read(inifile_path)

log_dir = inifile.get("dirs", "log_dir")

from visualize import plot

dt_fmt_date = '%Y-%m-%d'

settings_file = inifile.get("google_drive", "settings_file")
gd_csv_folder = inifile.get("google_drive", "gd_csv_folder")
gd_image_folder = inifile.get("google_drive", "gd_image_folder")

def upload_to_google_drive(filepath, folder_id):
    filename = os.path.basename(filepath)

    search_query = {
        "q": "'%s' in parents and trashed=false" % folder_id
    }

    gauth = GoogleAuth(settings_file=settings_file)
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    file_list = drive.ListFile(search_query).GetList()
    file_exists = False
    gdf_obj = None
    for f in file_list:
        if f['title'].encode('utf-8') == filename:
            file_exists = True
            gdf_obj = f

    if file_exists:
        gdf_obj.SetContentFile(filepath)
        gdf_obj.Upload()

    else:
        f = drive.CreateFile({'title': filename})
        f.SetContentFile(filepath)
        f.Upload()
        f['parents'] = [{"kind": "drive#fileLink", "id": folder_id}]
        f.Upload()

if __name__ == '__main__':

    tgt_day = []
    now = dt.now()
    td_1d = timedelta(days=1)
    tgt_day.append(now)
    tgt_day.append(now - td_1d)

    for day in tgt_day:
        for key in 'cpu', 'disk':
            d = day.strftime(dt_fmt_date)

            title = "Temperature(%s): %s" % (key, d)
            pngfile = os.path.join(log_dir, "temperature-%s-%s.png" % (key, d))
            csvfile = os.path.join(log_dir, "temperature-%s-%s.csv" % (key, d))

            if day == now:
                plot(key, day, title, pngfile, inc24h=True)
            else:
                plot(key, day, title, pngfile)
            upload_to_google_drive(pngfile, gd_image_folder)
            upload_to_google_drive(csvfile, gd_csv_folder)

