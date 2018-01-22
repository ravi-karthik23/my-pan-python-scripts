#!/bin/env/python

import os
import sys
import time
import netmiko
from netmiko import ConnectHandler
from getpass import getpass

device2={
    'device_type':'paloalto_panos',
    'ip':'192.168.50.1',
    'username':'admin1',
    'password':'admin1',
    'port':22,
    }

net_connect = ConnectHandler(**device2)
output = net_connect.send_command_expect("set cli pager off\n")

print(output)

output = net_connect.send_command_expect("show system info")
print(output)
time.sleep(5)

output = net_connect.send_command_expect("show counter global filter delta yes")
print(output)

output = net_connect.send_command_expect("show session all")
print(output)
