#!/bin/bash

case $1 in
    master)
        echo "Enter in master..." >> /var/log/notify.log
        echo "" > /var/lib/cloudmonitor/master
        exit 0
        ;;
    backup)
        echo "Enter in backup..." >> /var/log/notify.log
        rm -f /var/lib/cloudmonitor/master
        exit 0
        ;;
    fault)
        echo "Enter in fault..." >> /var/log/notify.log
        exit 0
        ;;
    *)
        echo "(`basename $0`(master|backup|fault)"
        exit 1
        ;;
esac
