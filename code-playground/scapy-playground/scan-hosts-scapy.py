# Command: python scan-hosts-scapy.py -t target_ip_range
# Example: python scan-hosts-scapy.py -t 192.168.0.0/24

import scapy.all as scapy
import argparse
# import socket


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target",
                        help="Target IP/IP Range")
    options = parser.parse_args()
    return options


def scan(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=5,  # NOTE: the timeout value has to be large in bad network
                              verbose=False)[0]

    clients_list = []
    for element in answered_list:
        client_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
        clients_list.append(client_dict)
    return clients_list


def print_result(results_list):
    print("IP\t\t\tMAC Address")
    print("----------------------------------------------------")
    for client in results_list:
        print(client["ip"] + "\t\t" + client["mac"])
        # print(client["ip"] + "\t\t" + client["mac"] + "\t\t" + socket.gethostbyaddr(client["ip"]))


options = get_arguments()
scan_result = scan(options.target)
print_result(scan_result)
