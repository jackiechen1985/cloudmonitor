#!/bin/bash

[[ `ps -ef | grep cloudmonitor | grep -v grep | wc -l` -ge 2 ]] && exit 0 || exit 1