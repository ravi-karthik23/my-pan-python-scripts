#! /bin/env/python

'''
This is my script to print the output of the tunnel flow nexthop, tunnel flow context and session details for port 4501 and the IP in question

./netmiko-tunnel-context-v3.py [-s firewall_hostname/ip-address] [-u username] [-p password]
    -s: hostname of the remote server to login
    -u: username to login
    -p: password to login

example:
   
   ./netmiko-tunnel-context-v3.py  -s 192.168.50.1 -u mylogin -p mypassword
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


def get_prompt(username,netmiko_ch):
	system_info_op = netmiko_ch.send_command('show system info')
	for line in system_info_op.splitlines():
		if 'hostname' in line:
			host_name=line.split(':')[1]
			host_name=host_name[1:]
	        prompt= username + '@' + host_name + '>'
	return prompt
	
	

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
    print('Attempting Login to the firewall')
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
    
	
	#create the operational mode prompt:
	fw_prompt=get_prompt(panfw['username'],net_connect)
	
	#print the output of 'show system info'
	print(fw_prompt + 'show system info')
	output=net_connect.send_command('show system info')
	print(output[5:])
	
    #setting off the cli pager
    print('\n*******Setting the cli pager off***********')
	print(fw_prompt + 'set cli pager off')
    net_connect.send_command_expect("set cli pager off\n")

    destination_of_session = raw_input('destinaion_ip_for_session:')
    
    try:
        while True:
	    
            #Print the keymgr list-sa
            print(fw_prompt + 'debug keymgr list-sa\n')
            output=net_connect.send_command_expect("debug keymgr list-sa\n")
            print(output[5:])
        
	        #Set the Target DP to S1DP0
			print(fw_prompt + 'set system setting target-dp s1dp0\n')
            output=net_connect.send_command_expect("set system setting target-dp s1dp0\n")
            print(output[5:])
	    
            #Print the output of the "show running tunnel flow next-hop"
            print(fw_prompt + 'show running tunnel flow nexthop\n')
            output=net_connect.send_command_expect("show running tunnel flow nexthop\n")
            print(output[5:])
       	    
	    
            #Extract the content-ID from the output of the "show running tunnel flow next-hop"
            tunn_flow_nh=[]
            context_id_list=[]
            tunn_flow_nh=output.splitlines()             ## Split the output as a list of strings de-limited by newlines
            for i in tunn_flow_nh:
                if 'SPI' in i:                           ## Search for 'SPI'
       	            context_id=int(i.split()[4])         ## Split the line into a list and get the context id number
                    context_id_list.append(context_id)
	    		
	    
            #Print the output of the "show running tunnel flow context with the context id"
            for c_id in context_id_list:
                print(fw_prompt + 'show running tunnel flow context ',c_id)
                output=net_connect.send_command_expect("show running tunnel flow context %d\n" %c_id)
                print(output[5:])
	    
            #Print the output of "show session all filter destination-port 4501"
            print(fw_prompt + 'show session all filter destination-port 4501')
            output=net_connect.send_command_expect("show session all filter destination-port 4501\n")
            print(output[5:])
	    
            #Print the output of "show session all filter destination <entered-ip> "
            print(fw_prompt + 'show session all filter destination ',destination_of_session)
            output=net_connect.send_command("show session all filter destination %s\n" %destination_of_session)
            print(output[5:])
		
	    
            #Set the Target DP to S1DP1
            print(fw_prompt + 'set system setting target-dp s1dp1\n')
            output=net_connect.send_command_expect("set system setting target-dp s1dp1\n")
            print(output[5:])
       	    
            #Print the output of the "show running tunnel flow next-hop"
            print(fw_prompt + 'show running tunnel flow nexthop\n')
            output=net_connect.send_command_expect("show running tunnel flow nexthop\n")
            print(output[5:])
	    
	    
			#Extract the content-ID from the output of the "show running tunnel flow next-hop"
            tunn_flow_nh=[]
            context_id_list=[]
            tunn_flow_nh=output.splitlines()             ## Split the output as a list of strings de-limited by newlines
            for i in tunn_flow_nh:
                if 'SPI' in i:                           ## Search for 'SPI'
       	            context_id=int(i.split()[4])         ## Split the line into a list and get the context id number
                    context_id_list.append(context_id)
	    		
			#Print the output of the "show running tunnel flow context with the context id"
            for c_id in context_id_list:
                print(fw_promt + 'show running tunnel flow context ',c_id)
                output=net_connect.send_command_expect("show running tunnel flow context %d\n" %context_id)
                print(output[5:])
	    
            #Print the output of "show session all filter destination-port 4501"
            print(fw_prompt + 'show session all filter destination-port 4501')
            output=net_connect.send_command_expect("show session all filter destination-port 4501\n")
            print(output[5:])
	    
            #Print the output of "show session all filter destination <entered-ip> "
            print(fw_prompt + 'show session all filter destination ',destination_of_session)
            output=net_connect.send_command("show session all filter destination %s\n" %destination_of_session)
            print(output[5:])
       	    
            #Print the output of "show clock"
            print('>show clock')
            output=net_connect.send_command("show clock\n")
            print(output)
	    
            time.sleep(5)
            
    except KeyboardInterrupt:
        #log out from the firewall and exit from the script
        print('Done and exiting the firewall and terminating the  script\n')
        print(time.ctime())
        net_connect.disconnect()
        raise SystemExit


if __name__ == '__main__':
    main()

    
