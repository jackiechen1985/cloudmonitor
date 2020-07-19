#!/usr/bin/python3

import sys
import os
import argparse
import random
import datetime
import time
import uuid
import multiprocessing


def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(
        description='ftp_data_generator.py is used to generate Fortinet/F5 PM data to ftp server.')
    parser.add_argument('-d', '--directory', required=True, help='ftp serve directory', dest='directory', type=str)
    parser.add_argument('-n', '--natgateway-directory', required=True, help='natgateway directory',
                        dest='natgateway_directory', type=str)
    parser.add_argument('-v', '--ipsecvpn-directory', required=True, help='ipsecvpn directory',
                        dest='ipsecvpn_directory', type=str)
    parser.add_argument('-b', '--loadbalancer-directory', required=True, help='loadbalancer directory',
                        dest='loadbalancer_directory', type=str)
    parser.add_argument('-l', '--loadbalance-listener-directory', required=True, help='loadbalance listener directory',
                        dest='loadbalance_listener_directory', type=str)
    parser.add_argument('-f', '--file-count', required=True, help='ftp file count to be generate for each PM type',
                        dest='file_count', type=int)
    parser.add_argument('-r', '--record-count', required=True, help='record count in each PM file',
                        dest='record_count', type=int)
    parser.add_argument('-i', '--interval', required=True, help='interval time for PM data generating', dest='interval',
                        type=int)

    args = parser.parse_args()
    return args


def clear_data(args):
    # Clear natgateway data
    if args.natgateway_directory:
        natgateway_directory_path = os.path.join(args.directory, args.natgateway_directory)
        if os.path.exists(natgateway_directory_path):
            for file in os.listdir(natgateway_directory_path):
                os.unlink(os.path.join(natgateway_directory_path, file))
        else:
            os.mkdir(natgateway_directory_path)

    # Clear ipsecvpn data
    if args.ipsecvpn_directory:
        ipsecvpn_directory_path = os.path.join(args.directory, args.ipsecvpn_directory)
        if os.path.exists(ipsecvpn_directory_path):
            for file in os.listdir(ipsecvpn_directory_path):
                os.unlink(os.path.join(ipsecvpn_directory_path, file))
        else:
            os.mkdir(ipsecvpn_directory_path)

    # Clear loadbalancer data
    if args.loadbalancer_directory:
        loadbalancer_directory_path = os.path.join(args.directory, args.loadbalancer_directory)
        if os.path.exists(loadbalancer_directory_path):
            for file in os.listdir(loadbalancer_directory_path):
                os.unlink(os.path.join(loadbalancer_directory_path, file))
        else:
            os.mkdir(loadbalancer_directory_path)

    # Clear loadbalance listener data
    if args.loadbalance_listener_directory:
        loadbalance_listener_directory_path = os.path.join(args.directory, args.loadbalance_listener_directory)
        if os.path.exists(loadbalance_listener_directory_path):
            for file in os.listdir(loadbalance_listener_directory_path):
                os.unlink(os.path.join(loadbalance_listener_directory_path, file))
        else:
            os.mkdir(loadbalance_listener_directory_path)


def generate_natgateway_file(natgateway_directory_path, record_count):
    natgateway_file_path = os.path.join(natgateway_directory_path, f'{int(time.time())}-NATPerformance.txt')
    with open(natgateway_file_path, 'x') as fp:
        for i in range(record_count):
            LogTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            Uuid = uuid.uuid1()
            connectNum = random.randint(0, 1000)
            dataPacketInNum = random.randint(0, 1000000)
            dataPacketOutNum = random.randint(0, 1000000)
            bandwidthIn = random.randint(0, 1000000)
            bandwidthOut = random.randint(0, 1000000)
            dataSource = f'{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.' \
                         f'{random.randint(0, 254)}'
            record = f'{LogTime};{Uuid};{connectNum};{dataPacketInNum};{dataPacketOutNum};{bandwidthIn};' \
                     f'{bandwidthOut};{dataSource}\n'
            fp.write(record)
            print(f'Write record: {record} to {natgateway_file_path}')


def generate_ipsecvpn_file(ipsecvpn_directory_path, record_count):
    ipsecvpn_file_path = os.path.join(ipsecvpn_directory_path, f'{int(time.time())}-IpsecVPNPerformance.txt')
    with open(ipsecvpn_file_path, 'x') as fp:
        for i in range(record_count):
            LogTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            Uuid = uuid.uuid1()
            bandwidthInTotal = random.randint(0, 1000000)
            bandwidthOutTotal = random.randint(0, 1000000)
            dataPacketInNumTotal = random.randint(0, 1000000)
            dataPacketOutNumTotal = random.randint(0, 1000000)
            dataSource = f'{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.' \
                         f'{random.randint(0, 254)}'
            record = f'{LogTime};{Uuid};{bandwidthInTotal};{bandwidthOutTotal};{dataPacketInNumTotal};' \
                     f'{dataPacketOutNumTotal};{dataSource}\n'
            fp.write(record)
            print(f'Write record: {record} to {ipsecvpn_file_path}')


def generate_loadbalancer_file(loadbalancer_directory_path, record_count):
    loadbalancer_file_path = os.path.join(loadbalancer_directory_path, f'EXP_PM_VLB_{int(time.time())}.txt')
    with open(loadbalancer_file_path, 'x') as fp:
        for i in range(record_count):
            CREATE_TIME = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ID = uuid.uuid1()
            TRAFFIC_IN = random.randint(0, 1000000)
            TRAFFIC_OUT = random.randint(0, 1000000)
            REQUESTS_TOTAL = random.randint(0, 1000000)
            ACTIVE_CON = random.randint(0, 1000)
            record = f'{CREATE_TIME};{ID};{TRAFFIC_IN};{TRAFFIC_OUT};{REQUESTS_TOTAL};{ACTIVE_CON}\n'
            fp.write(record)
            print(f'Write record: {record} to {loadbalancer_file_path}')


def generate_loadbalance_listener_file(loadbalance_listener_directory_path, record_count):
    loadbalance_listener_file_path = os.path.join(loadbalance_listener_directory_path,
                                                  f'EXP_PM_LISTENER_{int(time.time())}.txt')
    with open(loadbalance_listener_file_path, 'x') as fp:
        for i in range(record_count):
            CREATE_TIME = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ID = uuid.uuid1()
            TRAFFIC_IN = random.randint(0, 1000000)
            TRAFFIC_OUT = random.randint(0, 1000000)
            REQUESTS_TOTAL = random.randint(0, 1000000)
            ACTIVE_CON = random.randint(0, 1000)
            ESTAB_CON = random.randint(0, 1000)
            PACKET_IN = random.randint(0, 1000000)
            PACKET_OUT = random.randint(0, 1000000)
            ABANDON_CON = random.randint(0, 1000)
            HTTP_QPS = random.randint(0, 1000000)
            record = f'{CREATE_TIME};{ID};{TRAFFIC_IN};{TRAFFIC_OUT};{REQUESTS_TOTAL};{ACTIVE_CON};{ESTAB_CON};' \
                     f'{PACKET_IN};{PACKET_OUT};{ABANDON_CON};{HTTP_QPS}\n'
            fp.write(record)
            print(f'Write record: {record} to {loadbalance_listener_file_path}')


def generate_natgateway_data(args):
    if args.natgateway_directory:
        for i in range(args.file_count):
            generate_natgateway_file(os.path.join(args.directory, args.natgateway_directory), args.record_count)
            time.sleep(args.interval)


def generate_ipsecvpn_data(args):
    if args.ipsecvpn_directory:
        for i in range(args.file_count):
            generate_ipsecvpn_file(os.path.join(args.directory, args.ipsecvpn_directory), args.record_count)
            time.sleep(args.interval)


def generate_loadbalancer_data(args):
    if args.loadbalancer_directory:
        for i in range(args.file_count):
            generate_loadbalancer_file(os.path.join(args.directory, args.loadbalancer_directory), args.record_count)
            time.sleep(args.interval)


def generate_loadbalance_listener_data(args):
    if args.loadbalance_listener_directory:
        for i in range(args.file_count):
            generate_loadbalance_listener_file(os.path.join(args.directory, args.loadbalance_listener_directory),
                                               args.record_count)
            time.sleep(args.interval)


def main():
    args = get_args()
    if not os.path.exists(args.directory):
        print(f'{args.directory} does not exist')
        sys.exit(1)

    if args.file_count <= 0:
        print('file_count must larger than 0')

    if args.record_count <= 0:
        print('record_count must larger than 0')

    if args.interval <= 0:
        print('interval must larger than 0')

    clear_data(args)

    natgateway_process = multiprocessing.Process(target=generate_natgateway_data, args=(args,))
    ipsecvpn_process = multiprocessing.Process(target=generate_ipsecvpn_data, args=(args,))
    loadbalancer_process = multiprocessing.Process(target=generate_loadbalancer_data, args=(args,))
    loadblance_listener_process = multiprocessing.Process(target=generate_loadbalance_listener_data, args=(args,))

    natgateway_process.start()
    ipsecvpn_process.start()
    loadbalancer_process.start()
    loadblance_listener_process.start()

    natgateway_process.join()
    ipsecvpn_process.join()
    loadbalancer_process.join()
    loadblance_listener_process.join()


# Start program
if __name__ == '__main__':
    main()
