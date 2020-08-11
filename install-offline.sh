#!/bin/bash

rpm -Uvh pkgs/cloudmonitor-node/*.rpm --force

mkdir -p ~/.pip
cp -f pip.conf ~/.pip
pip3 install --use-wheel --no-index --find-links=pkgs/cloudmonitor-node -r requirements.txt

python3 setup.py install

mkdir -p /var/log/cloudmonitor
mkdir -p /etc/cloudmonitor
cp -f cloudmonitor.conf /etc/cloudmonitor/
cp -f task.json /etc/cloudmonitor/
cp -f cloudmonitor.service /usr/lib/systemd/system/

cp -f keepalived.conf /etc/keepalived/
cp -f health_check.sh /etc/keepalived/
cp -f notify.sh /etc/keepalived/

systemctl enable keepalived
systemctl enable cloudmonitor