# rpi_temp_monitor

raspberry piの温度を監視するためのスクリプト

## sampling.py

CPUとディスクから情報を取得するスクリプト。
情報は一時的にpickleオブジェクトに格納する。
定期的にpickleオブジェクトの情報を集約し、
ある期間の平均値/最大値/最小値をcsv形式でファイルに出力する。
cronで定期的に起動するよう設定する。(1~2分に1度程度を想定)

## visualize.py

sampling.pyが集約・出力した情報をもとに、データを可視化するスクリプト。
ライブラリなので、直接は呼び出されない。

## googledrive.py

定期的にサンプルしたデータとグラフをgoogleドライブに格納する。
cronで定期的に起動するよう設定する。(1日に1度程度を想定)

## twitter.py

twitterのmentionを確認し、応答をする。
『温度』という文字列があったら温度情報をグラフ付きで返す。
特にキーワードがなかったらgreetings.yamlから適当な挨拶を返す。
サービスではないので、cronで定期的に呼びだす。(1分に1回を想定)

# 使い方

設定など

## rpi\_temp\_monitor.ini

設定ファイル。
.sampleのファイルをベースに新規作成すること。

## settings.yaml

googledriveを使うための設定ファイル

https://pythonhosted.org/PyDrive/oauth.html

## words.yaml

twitterでやり取りするメッセージ集。
以下のようなセクションで構成。

- greeting: twitterでmentionがあり、特にキーワードがなかった場合に、このリストから一つ応答を返す。
- temperature: ユーザがこのリストに含まれている言葉でmentionしてきた場合、温度情報を返す
- shutdown: ユーザがこのリストに含まれている言葉でmentionしてきた場合、シャットダウンする
- reboot: ユーザがこのリストに含まれている言葉でmentionしてきた場合、再起動する

## crontab

crontabでの設定例

```
*  *  *  *  * root /opt/rpi_temp_monitor/sampling.py
*  *  *  *  * root /opt/rpi_temp_monitor/twitter.py
0   17  *  *  * root /opt/rpi_temp_monitor/googledrive.py
```



