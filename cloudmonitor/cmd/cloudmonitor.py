import argparse

from cloudmonitor import config
from cloudmonitor import task_scheduler


def main():
    config.init_configuration()
    ts = task_scheduler.TaskScheduler()
    ts.start()


if __name__ == "__main__":
    main()
