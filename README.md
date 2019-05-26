# rpi_temp_monitor

raspberry piの温度を監視するためのスクリプト

# 使い方

## configuration.py

プロジェクトディレクトリにconfiguration.pyが必要。
以下の情報を含めること

```
# cat configuration.py
gd_csv_folder = "Google Drive Folder ID"
gd_image_folder = "Google Drive Folder ID"
settings_file = "Settings file for Google API"
log_dir = 'Directory to output samples'
pklfile = 'Directory to store pickle file'
```

## settings.yaml

同じくプロジェクトディレクトリにsettings.yamlが必要。

https://pythonhosted.org/PyDrive/oauth.html

## crontab

crontabで動作を指定する。

```
*/2  *  *  *  * root /opt/rpi_temp_monitor/sampling.py
0   17  *  *  * root /opt/rpi_temp_monitor/visualize.py
```



