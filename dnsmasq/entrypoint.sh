#!/bin/bash

echo "server=8.8.8.8" >> /etc/dnsmasq.conf
echo "addn-hosts=/etc/dnsmasq_static_hosts" >> /etc/dnsmasq.conf

dnsmasq --pid-file=/tmp/dnsmasq.pid

export DNSMASQ_PID=`cat /tmp/dnsmasq.pid`
export DNSMASQ_HOSTFILE=/etc/dnsmasq_static_hosts
python /cns.py
