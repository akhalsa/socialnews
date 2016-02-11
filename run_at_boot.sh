#!/bin/sh

pushd /home/ubuntu/socialnews/
python tornado_host.py --mysql_host=1 &
python tweepy_scanner.py --mysql_host=1 &
python data_processing.py --mysql_host=1 &
popd