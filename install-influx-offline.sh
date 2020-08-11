#!/bin/bash

rpm -Uvh pkgs/influxdb-node/influxdb-1.8.0.x86_64.rpm --force

cp -f influxdb.conf /etc/influxdb/

systemctl enable influxdb
systemctl restart influxdb

sleep 10

influx -execute "CREATE USER "cloudmonitor" WITH PASSWORD 'cloudmonitor'"
influx -execute 'create database cloudmonitor'
influx -execute 'ALTER RETENTION POLICY "autogen" ON "cloudmonitor" DURATION 12h SHARD DURATION 6h DEFAULT'