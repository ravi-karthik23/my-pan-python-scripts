#! /bin/env/python

'''
This is my script to log into the firewall and create 19 routes and commit the changes to the firewall

./netmiko-route-range-commit.py [-s firewall_hostname/ip-address] [-u username] [-p password]
    -s: hostname of the remote server to login
    -u: username to login
    -p: password to login

example:
   This script creates 19 routes from test64 to test83 :
   ./netmiko-route-range-commit.py -s 192.168.50.1 -u mylogin -p mypassword
'''


import os
import sys
import time
import netmiko
from netmiko import ConnectHandler
import getopt
import getpass


try:
    raw_input
except NameError:
    raw_input = input

def exit_with_usage():
    print(globals()['__doc__'])
    os._exit(1)


def main():
    #######################################################
    ## Parse the options,arguments, get ready, etc
    ######################################################

    try:
        optlist,args = getopt.getopt(sys.argv[1:], 'h?s:u:p:',['help','h','?'])
    except Exception as e:
        print(str(e))
        exit_with_usage()

    options = dict(optlist)

    if len(args) > 1:
        exit_with_usage()
    if [elem for elem in options if elem in ['-h','--h','-?','--?','--help']]:
        print("Help:")
        exit_with_usage()

    if '-s' in options:
        hostname = options['-s']
    else:
        hostname = raw_input('hostname:')
        
    if '-u' in options:
        username = options['-u']
    else:
        username = raw_input('username:')

    if '-p' in options:
        password = options['-p']
    else:
        password = getpass.getpass('password:')

    
    #defining the parameters to create the login 
    panfw={
        'device_type':'paloalto_panos',
        'ip':hostname,
        'username':username,
        'password':password,
        'port':22}

    #connecting to the firewall. Raise the appropriate Exceptions and exit ouut from the program if the information provided is inoorrect

    try:
        net_connect = ConnectHandler(**panfw)
    except netmiko.ssh_exception.NetMikoTimeoutException:
        print('Connection to the firewall with IP/hostname %s timed out.Please check the IP/Hostname or the route to this device again',panfw['ip'] )
        raise SystemExit
    except netmiko.ssh_exception.NetMikoAuthenticationException:
        print('The credentials provided were incorrect. Please verify the username,password or both.')
        print('Credentials fed: username:%s, password:%s ',panfw['username'],panfw['password'])
        raise SystemExit
    else:
        print('Logged in Successfully at ',time.ctime())

    #setting off the cli pager
    print('\nSetting the cli pager off:')
    net_connect.send_command_expect("set cli pager off\n")


    #setting the config-output-format to set
    print('setting the config output format to set:')
    net_connect.send_command_expect('set cli config-output-format set')


    #print the config diff
    print('print the initial config diff:')
    output = net_connect.send_command_expect('show config diff')
    print(output)


    #creating a list of 200 strings that are set commands for 200 unique routes
    route_list=[]
    print('creating the static routes:\n')
    for i in range(84,104):
        route_list.append('set network virtual-router default routing-table ip static-route test%d destination 2.2.2.%d/32 interface ethernet1/1 nexthop ip-address 1.1.1.2' %(i,i))

    #print all the routes created!    
    [print(i) for i in route_list]     


    #add each set command for each of these routes to the firewall
    print('Adding each of these static routes to the candidate configuration:\n')
    for i in range(len(route_list)):
        net_connect.send_config_set(route_list[i])


    #committing the config
    try:
        print('Committing the config')
        net_connect.commit()
    except OSError:
        print('config committed')
    finally:
        print('exit the config mode')

    #exiting config mode
    print('Exiting the config mode')
    net_connect.exit_config_mode()


    #print the jobs summary for the commit
    print('printing the output of "show jobs all"')
    output = net_connect.send_command_expect('show jobs all')
    print(output)

    #log out from the firewall and exit from the script
    print('Done and exiting the firewall and terminating the  script\n')
    print(time.ctime())
    net_connect.disconnect()
    raise SystemExit


if __name__ == '__main__':
    main()
