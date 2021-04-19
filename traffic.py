r"""
traffic is a command line tool to simulate traffic between endpoints
Usage:
traffic simulate <start-host-id-range> <end-host-id-range>
traffic flood <dest-host-id>
traffic test <ip-address>
traffic (-h | --help)
traffic
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import math
import os
import subprocess
from random import randrange
from docopt import docopt
from scapy.all import *

__version__ = '0.0.1'

def generate_ip(first=None, second=None, third=None, fourth=None, exclude_list=None):
    if first == None:
        first = randrange(1, 256)
    if second == None:
        second = randrange(1, 256)
    if third == None:
        third = randrange(1, 256)
    if type(fourth) == type((1,1)):
        if len(fourth) == 2:
            fourth = randrange(int(fourth[0]), int(fourth[1]))
        else:
            print("Please enter range as (1, 64)")
    elif fourth == None:
        fourth = randrange(1, 256)
    ip = str(first) + '.' + str(second) + '.' + str(third) + '.' + str(fourth)
    return ip

def get_interface():
    interface = os.popen('ifconfig | awk \'/eth0/ {print $1}\'').read().split(':')[0]
    if interface == '':
        print('Ethernet interface doesn\'t exist. Exiting...')
        exit(-2)
    return interface

def dos(dst_ip):
    # hping3 gives the best DOS performance
    dos_command = 'sudo hping3 ' + dst_ip + ' -S -p 80 --flood'
    print(dos_command)
    p = subprocess.Popen(dos_command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()  
    p_status = p.wait()

def send_packets(dst_ip, verbose=False):
    packet = IP(dst=dst_ip, src=RandIP())/TCP(dport=80, sport=RandShort(), flags='S')
    send(packet, verbose=verbose, inter=0.025, loop=1)

def simulate(start_host_id_range, end_host_id_range):
    print('Simulating traffic on IPs in range 10.0.0.' + str(start_host_id_range) + \
                                        ' and 10.0.0.' + str(end_host_id_range))
    dst_ip = generate_ip(first=10,
                            second=0,
                            third=0,
                            fourth=(start_host_id_range, end_host_id_range))
    print('Destination IP: ' + dst_ip + '\n')
    send_packets(dst_ip)

def flood(dest_host_id):
    print('Flooding ' + str(dest_host_id))
    dst_ip = generate_ip(first=10,
                            second=0,
                            third=0,
                            fourth=dest_host_id)
    print('Destination IP: ' + dst_ip)
    dos(dst_ip)

def main():
    if os.name == 'nt':
        print('Executes on Unix-like operating systems only. Exiting...')
        exit(-1)
    arguments = docopt(__doc__, version = __version__)
    if arguments['simulate']:
        simulate(arguments['<start-host-id-range>'], arguments['<end-host-id-range>'])
    elif arguments['flood']:
        flood(arguments['<dest-host-id>'])
    else:
        print(__doc__)

if __name__ == '__main__':
    main()