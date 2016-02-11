#! /bin/sh
# /etc/init.d/run_at_boot.sh

case "$1" in
  start)
    echo "**************Filtra Deployment Start"
    # run application you want to start
    cd /home/ubuntu/socialnews/
    python tornado_host.py &
    python tweepy_scanner.py &
    python data_processing.py &
    echo "******************Filtra DEPLOYED"
    ;;
  stop)
    echo "Stopping example"
    # kill application you want to stop
    killall python
    ;;
  *)
    exit 1
    ;;
esac

exit 0
