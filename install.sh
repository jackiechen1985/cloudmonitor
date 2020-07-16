#!/bin/bash

yum install -y python3 python3-devel gcc keepalived

mkdir -p ~/.pip
cp -f pip.conf ~/.pip

pip3 install -r requirements.txt

python3 setup.py install

mkdir -p /var/log/cloudmonitor
mkdir -p /etc/cloudmonitor
cp -f cloudmonitor.conf /etc/cloudmonitor/
cp -f task.json /etc/cloudmonitor/
cp -f cloudmonitor.service /usr/lib/systemd/system/

cp -f keepalived.conf /etc/keepalived/
cp -f health_check.sh /etc/keepalived/
cp -f notify.sh /etc/keepalived/