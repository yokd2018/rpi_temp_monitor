#!/usr/bin/python
# coding: utf-8

import random
import base64
import datetime
import urllib
import hmac
import hashlib
import subprocess
import requests
import re
import json
import ConfigParser
import yaml
import random
import os
import pickle
from datetime import datetime as dt
from sampling import get_current_temperature
from visualize import plot

inifile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rpi_temp_monitor.ini")
inifile = ConfigParser.SafeConfigParser()
inifile.read(inifile_path)

creds = dict(inifile.items("twitter_creds"))
basedir = inifile.get("dirs", "basedir")
pklfile = os.path.join(basedir, 'twitter_id.pkl')

dt_fmt_date = '%Y-%m-%d'

class MyTwitterClient(object):
    def __init__(self, method, url, params={}, headers={}):
        self.method = method.upper()
        self.url = url

        r32int = "".join([str(random.randint(0,9)) for _ in range(32)])
        self.oauth_nonce = re.sub('[0-9+/=]', '', base64.b64encode(r32int))

        self.oauth_timestamp = datetime.datetime.now().strftime('%s')
        self.params = params
        self.headers = headers


    def get_oauth_signature(self):
        params = {
          "oauth_consumer_key": creds["oauth_consumer_key"],
          "oauth_nonce": self.oauth_nonce,
          "oauth_signature_method": "HMAC-SHA1",
          "oauth_timestamp": self.oauth_timestamp,
          "oauth_token": creds["oauth_token"],
          "oauth_version": "1.0"
        }
        image_upload = False
        params.update(self.params)
        if params.has_key('imgpath'):
            image_upload = True
            params.pop('imgpath')

        param_str = []
        for k in sorted(params.keys()):
            ek = urllib.quote(k, safe='')
            ev = urllib.quote(params[k], safe='')
            s = '%s=%s' % (ek, ev)
            param_str.append(s)
        agg_param = '&'.join(param_str)

        enc_url = urllib.quote(self.url, safe='')
        enc_param = urllib.quote(agg_param, safe='')
        sign_str = "&".join([self.method, enc_url, enc_param])

        ecs = urllib.quote(creds["oauth_consumer_secret"], safe='')
        ets = urllib.quote(creds["oauth_token_secret"], safe='')
        sign_key = '&'.join([ecs,ets])

        return base64.b64encode(hmac.new(sign_key, sign_str, hashlib.sha1).digest())

    def get_oauth_header_string(self):
        ret = "OAuth %s"
        param_str = []
        params = {
          "oauth_consumer_key": creds["oauth_consumer_key"],
          "oauth_nonce": self.oauth_nonce,
          "oauth_signature": self.get_oauth_signature(),
          "oauth_signature_method": "HMAC-SHA1",
          "oauth_timestamp": self.oauth_timestamp,
          "oauth_token": creds["oauth_token"],
          "oauth_version": "1.0"
        }
        for k,v in params.items():
            ek = urllib.quote(k, safe='')
            ev = urllib.quote(v, safe='')
            s = '%s="%s"' % (ek, ev)
            param_str.append(s)
        return ret % ', '.join(param_str)

    def issue(self):
        headers = {
            "Authorization": self.get_oauth_header_string()
        }
        headers.update(self.headers)
        if self.params.has_key('imgpath'):
            files = {"media" : open(self.params['imgpath'], 'rb')}
            r = requests.post(self.url, headers=headers, files=files)
        elif self.method == 'GET':
            r = requests.get(self.url, headers=headers, params=self.params)
        elif self.method == 'POST':
            r = requests.post(self.url, headers=headers, params=self.params)
        if r.status_code > 300:
            print "HTTP request failed status code: %s" % str(r.status_code)
            for k,v in r.headers.items():
                print '%s: %s' % (k,v)
            r.raise_for_status()
        return r.json()

def save_pkl(data):
    with open(pklfile, 'wb') as f:
        pickle.dump(data, f)

def load_pkl():
    try:
        with open(pklfile, 'rb') as f:
            data = pickle.load(f)

    except:
        data = ""

    return data

def tweet_response(tweet):
    if "温度" in tweet['text'].encode('utf-8'):
        post_temperature(tweet)
    else:
        post_greeting(tweet)


def main():
    since_id = load_pkl()
    tweets = get_mention_tl(since_id)

    if since_id == "":
        since_id = tweets[-1]['id_str']
        save_pkl(since_id)
        return

    for t in reversed(tweets):
        tweet_response(t)
        since_id = t['id_str']

    save_pkl(since_id)

def get_mention_tl(since_id):
    task = {
        'method': 'get',
        'url': "https://api.twitter.com/1.1/statuses/mentions_timeline.json",
        'params': {}
    }
    if since_id != "":
        task['params']['since_id'] = since_id

    c = MyTwitterClient(**task)
    return c.issue()

def post_greeting(tweet):
    greetings_file = os.path.join(basedir, "greetings.yaml")
    with open(greetings_file, "r") as f:
        data = yaml.load(f)
    referer = tweet['user']['screen_name'].encode('utf-8')
    msg= "@%s %s" % (referer, data[random.randint(0, len(data)-1)].encode('utf-8'))
    print msg
    task = {
        'method': 'post',
        'url': "https://api.twitter.com/1.1/statuses/update.json",
        'params': {
            "status": msg,
            "in_reply_to_status_id": tweet['id_str']
        }
    }
    c = MyTwitterClient(**task)
    return c.issue()

def post_temperature(tweet):

    now = dt.now()

    media_ids = []
    for key in 'cpu', 'disk':
        d = now.strftime(dt_fmt_date)

        title = "Temperature(%s): %s" % (key, d)
        pngfile = os.path.join('/tmp/', "temperature-%s-%s.png" % (key, d))
        plot(key, now, title, pngfile, inc24h=True)

        data = post_tweet_media(pngfile)
        media_ids.append(data["media_id_string"])

    s = get_current_temperature()
    referer = tweet['user']['screen_name'].encode('utf-8')
    msg = "@%s %s現在の温度は、cpu: %s度, disk: %s度です！" % \
          (tweet['user']['screen_name'].encode('utf-8'), \
           now.strftime('%H時%M分%S秒'), s.data['cpu'], s.data['disk'])

    task = {
        'method': 'post',
        'url': "https://api.twitter.com/1.1/statuses/update.json",
        'params': {
            "status": msg,
            "media_ids": ','.join(media_ids),
            "in_reply_to_status_id": tweet['id_str']
        }
    }

    c = MyTwitterClient(**task)
    return c.issue()

def post_tweet_media(imgpath):
    task = {
        'method': 'post',
        'url': "https://upload.twitter.com/1.1/media/upload.json",
        'params': {"imgpath": imgpath},
    }

    c = MyTwitterClient(**task)
    return c.issue()

if __name__ == '__main__':
    main()



