#!/bin/env/python

'''
This Script is to log into the firewall and print the output of the commands "show session all" and "show counter global filter delta yes" to the log file specified.
'''


import os
import sys
import time
import netmiko
from netmiko import ConnectHandler
from getpass import getpass

file2=open('logfill.txt','a')

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
for line in output:
    file2.write(line)

output = net_connect.send_command_expect("show session all")
for line in output:
    file2.write(line)


file2.close()

output = net_connect.send_command_expect("exit")
print(output)

print('termination script')
