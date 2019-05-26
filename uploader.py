from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os.path
import configuration as CONF

settings_file = CONF.settings_file

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
    f = 'test.txt'
    upload_to_google_drive(f)

