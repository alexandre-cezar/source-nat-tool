__author__ = 'Alexandre S. Cezar - acezar@juniper.net'

import sys
import socket
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *

# Variables Definition
file_input = 'nat_parameters.txt'
srx_parameters=list()

# Getting the data from the Input file
print "Trying to open the input file", file_input
try:
    f_open = open(file_input, 'r')
except:
    print "Error, input file not found", f_open
    quit()
print "Input file found, proceding"

# Parse the Input File to get the variables and values
print "Initializating file parsing"
for line in f_open:
    line = line.lstrip()
    if len(line) < 1 : continue
    line.find ('=')
    srx_values = line.split()
    srx_parameters.append(srx_values[2])
f_open.close()
print "Parsing sucessfully finished, proceding"

# DNS Resolution (resolving the input domain "var domain" into ip addresses)
ip_list = list()
try:
    ip_list = socket.gethostbyname_ex(srx_parameters[0])
    print "Resolving addresses for domain", srx_parameters[0]
except socket.gaierror, err:
    print "Domain resolution error, please check the network conectivity"
    ip_list = ()
if ip_list != ():
    print "Domain name resolved"
else:
    print "Error: List of IP address is empty"
    exit()

# Initial list clean up section (ip_list contains ips and words, need to filter)
cleaned_ip_list = ip_list[2]
print "Resolved IP addresses ", cleaned_ip_list

# Creating the Junos Template Config file
print "Creating Junos Template Config. file"
try:
    file = open("srx_nat_config.conf", "w")
    b=1
    for i in range(len(cleaned_ip_list)):
        file.write('set security nat source rule-set {} from zone {}\n'.format(srx_parameters[7], srx_parameters[5]))
        file.write('set security nat source rule-set {} to zone {}\n'.format(srx_parameters[7], srx_parameters[6]))
        file.write('set security nat source rule-set {} rule {}{} match source-address {}\n'.format(srx_parameters[7], srx_parameters[8], b, srx_parameters[4]))
        file.write('set security nat source rule-set {} rule {}{} match destination-address {}\n'.format(srx_parameters[7], srx_parameters[8], b, cleaned_ip_list[i]))
        file.write('set security nat source rule-set {} rule {}{} then source-nat interface\n'.format(srx_parameters[7], srx_parameters[8], b))
        b=b+1
    file.close()
except  err as e:
    print "Error creating the Junos Template Config. file"
    print (e)
print "Template file created sucessfully"

# Connecting to the selected SRX (var srx_management)
print 'Establishing connection to: ', srx_parameters[1]
dev = Device(host=srx_parameters[1], user=srx_parameters[2], password=srx_parameters[3])
try:
    dev.open()
except ConnectError:
    print "Could not connect to the SRX, please check your connectivity"
    exit()
print 'Connected'

# Locking the Configuration
cu = Config(dev)
print "Locking the configuration"
try:
    cu.lock()
except LockError as e:
    print "Error: Unable to lock configuration"
    print (e)
    dev.close()
    exit()

# Loading the Configuration file
print "Uploading objects and NAT rules"
try:
    conf_file = "./srx_nat_config.conf"
    cu.load(path=conf_file, format='set', merge=True)
except ConfigLoadError as e:
    print "Error: Unable to load the configuration"
    print (e)
    cu.unlock()
    dev.close()
    exit()

#Commiting the Configuration
print "Commiting the configuration"
try:
    cu.commit()
except CommitError as e:
    print "Error: Unable to commit the configuration"
    print "Executing the rollback 0 command"
    cu.rollback(rb_id=0)
    cu.commit()
    print (e)
    cu.unlock()
    dev.close()
    exit()

#Unlocking the Configuration
print "Unlocking the configuration"
try:
    cu.unlock()
except LockError as e:
    print "Error: Unable to lock configuration"
    print (e)
    dev.close()
    exit()

# Closing Connection to the SRX device
print 'Closing Connection to :', srx_parameters[1]
try:
    dev.close()
except ConnectError as e:
    print "Error on disconnecting from the SRX"
    print (e)
    exit()
print 'All Done. Tks for your preference'