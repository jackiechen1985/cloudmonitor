#!/bin/bash

yum install -y python3 python3-devel gcc

mkdir -p ~/.pip
cat >~/.pip/pip.conf <<EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
disable-pip-version-check = true
EOF

pip3 install -r requirements.txt

python3 setup.py install

mkdir -p /var/log/cloudmonitor
mkdir -p /etc/cloudmonitor
cat >/etc/cloudmonitor/cloudmonitor.conf <<EOF
[DEFAULT]
debug=True

[database]
connection=mysql+pymysql://cloudmonitor:cloudmonitor@127.0.0.1/cloudmonitor

[influxdb]
url=http://localhost:8086
username=cloudmonitor
password=cloudmonitor
database=cloudmonitor
retention_policy=autogen
organization=nokia

[rocketmq]
namesrv_addr=localhost:9876
producer_group=iam-cloud-producer
cm_topic=iam-cloud-bc-configure-topic
pm_topic=iam-cloud-bc-performance-topic

[ftp]
host=localhost
port=21
connection_timeout=60
username=ftp
password=ftp
nat_dir=/pub/nat
ipsec_dir=/pub/ipsec
vlb_dir=/pub/vlb
vlb_listener_dir=/pub/vlb_listener

[task_scheduler]
task_conf_path=/etc/cloudmonitor/task.json

[high_availability]
enable=True
host_ip=1.1.1.2
vip=1.1.1.1
EOF

cat >/etc/cloudmonitor/task.json <<EOF
[
    {
        "type": "periodic",
        "interval": 60,
        "initial_delay": 0,
        "module": "cloudmonitor.subtasks.nat_pm_collector.NatPmCollector"
    },
    {
        "type": "periodic",
        "interval": 300,
        "initial_delay": 60,
        "module": "cloudmonitor.subtasks.nat_pm_producer.NatPmProducer"
    },
    {
        "type": "periodic",
        "interval": 60,
        "initial_delay": 0,
        "module": "cloudmonitor.subtasks.ipsec_vpn_pm_collector.IpsecVpnPmCollector"
    },
    {
        "type": "periodic",
        "interval": 300,
        "initial_delay": 60,
        "module": "cloudmonitor.subtasks.ipsec_vpn_pm_producer.IpsecVpnPmProducer"
    },
    {
        "type": "periodic",
        "interval": 60,
        "initial_delay": 0,
        "module": "cloudmonitor.subtasks.vlb_pm_collector.VlbPmCollector"
    },
    {
        "type": "periodic",
        "interval": 300,
        "initial_delay": 60,
        "module": "cloudmonitor.subtasks.vlb_pm_producer.VlbPmProducer"
    },
    {
        "type": "periodic",
        "interval": 60,
        "initial_delay": 0,
        "module": "cloudmonitor.subtasks.vlb_listener_pm_collector.VlbListenerPmCollector"
    },
    {
        "type": "periodic",
        "interval": 300,
        "initial_delay": 60,
        "module": "cloudmonitor.subtasks.vlb_listener_pm_producer.VlbListenerPmProducer"
    }
]
EOF

cat >/usr/lib/systemd/system/cloudmonitor.service <<EOF
[Unit]
Description=CMCC Cloud Monitor
After=syslog.target network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/cloudmonitor --config-file /etc/cloudmonitor/cloudmonitor.conf --log-file /var/log/cloudmonitor/cloudmonitor.log
PrivateTmp=true
KillMode=process
Restart=on-failure
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
