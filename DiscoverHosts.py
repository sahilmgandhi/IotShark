import subprocess
import re
import sys
import scapy.all as scapy
from tabulate import tabulate

RESIDENTIAL_SUBNETS = [
    {'subnet_mask': '192.168.0.0/24', 'gateway': '192.168.0.1'},
    {'subnet_mask': '192.168.1.0/24', 'gateway': '192.168.1.1'},
    {'subnet_mask': '192.168.2.0/24', 'gateway': '192.168.2.1'},
    {'subnet_mask': '192.168.3.0/24', 'gateway': '192.168.3.1'},
    {'subnet_mask': '192.168.4.0/24', 'gateway': '192.168.4.1'},
    {'subnet_mask': '192.168.5.0/24', 'gateway': '192.168.5.1'},
    {'subnet_mask': '192.168.6.0/24', 'gateway': '192.168.6.1'},
    {'subnet_mask': '192.168.7.0/24', 'gateway': '192.168.7.1'},
    {'subnet_mask': '192.168.8.0/24', 'gateway': '192.168.8.1'},
    {'subnet_mask': '192.168.9.0/24', 'gateway': '192.168.9.1'},
    {'subnet_mask': '192.168.10.0/24', 'gateway': '192.168.10.1'}
]


def discover_host_info(ip):
    """
    Discover the OS and hardware vendor of the given host IP using nmap. Requires root
    """
    # For faster debugging only
    # if ip != '192.168.0.215':
    #     return { 'vendor': '(Not Discovered)', 'os_name': '(Not Discovered)'}

    pipe = subprocess.Popen(['nmap', '-sS', '-O', ip], stdout=subprocess.PIPE)
    nmap_stdout = pipe.communicate()[0].decode('utf-8').split('\n')

    vendor, os_name = None, None
    # 1 - hardware vendor of the host
    for line in nmap_stdout:
        regex_match = re.search(
            "MAC Address: .{2}:.{2}:.{2}:.{2}:.{2}:.{2} \((.*)\)", line)
        if regex_match:
            vendor = regex_match.group(1)
            break

    # 2 - OS the host is running
    for line in nmap_stdout:
        regex_match = re.search("OS details: (.*)", line)
        if regex_match:
            os_name = regex_match.group(1)
            break

    return {
        'vendor': vendor if vendor is not None else '(Not Found)',
        'os_name': os_name if os_name is not None else '(Not Found)'}


# Scan for all hosts in the given subnet
def scan_hosts(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=5,  # NOTE: the timeout value has to be large in bad network
                              verbose=False)[0]

    if len(answered_list) == 0:
        return answered_list
    print("Host scanning completed. {} hosts found.".format(len(answered_list)))

    clients_list = []
    for index, element in enumerate(answered_list):
        ip, mac = element[1].psrc, element[1].hwsrc
        print("Discovering host #{}: {}".format(index, ip))

        client_dict = {"ip": ip, "mac": mac}
        client_dict.update(discover_host_info(ip))
        clients_list.append(client_dict)
    return clients_list

# Print a table of discovered hosts


def print_result(results_list):
    print(
        tabulate([[str(index), client["ip"], client["mac"], client["vendor"], client["os_name"]] for index, client in enumerate(results_list)],
                 headers=['ID', 'IP Address', 'MAC Address', 'Vendor', 'Operating System']))

# Given the script's arguments, perform hosts scan and discovery if necessary and prompt the user to select the target host


def select_device(options):
    target, gateway = options.target, options.gateway
    if target is not None and gateway is not None:
        return target, gateway

    if options.scan is not None and gateway is not None:
        scan_result = scan_hosts(options.scan)
    else:
        print("No target, gateway or scanning subnet is provided. Proceed with scanning on common residential subnets.")
        for subnet in RESIDENTIAL_SUBNETS:
            print(f"Scanning gateway: {subnet['gateway']} ...")
            gateway = subnet['gateway']
            scan_result = scan_hosts(subnet['subnet_mask'])
            if len(scan_result) > 0:
                break
    if len(scan_result) == 0:
        print("No host found on the provided IP range or common residential subnet IPs.")
        sys.exit(0)
    print_result(scan_result)

    while True:
        print("Please select your IoT device by its ID: ")
        device_id = input()
        try:
            target = scan_result[int(device_id)]["ip"]
            break
        except Exception as e:
            print(e + " Please try again.")
    return target, gateway
