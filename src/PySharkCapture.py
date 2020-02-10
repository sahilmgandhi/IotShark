import pyshark
import csv
import threading
import time
# import test.test__osx_support
import os


class PySharkCapture(threading.Thread):
    def __init__(self, target_ip, file_timestamp):
        """
        Constructor

        @param  target_ip       The target IP address to intercept
        """
        threading.Thread.__init__(self)
        self.restore_flag = threading.Event()

        self.target_ip = target_ip
        curr_path = os.path.dirname(__file__)
        output_file_name = "csv/packetdump_" + \
            str(target_ip) + "_" + file_timestamp + ".csv"

        abs_file_path = os.path.join(curr_path, output_file_name)
        self.session_information = SessionInformation(abs_file_path)

        # Start capturing data
        self.capture = pyshark.LiveCapture(interface='en0')
        self.capture.set_debug()
        self.capture.sniff(timeout=5)

    def run(self):
        """
        Entrypoint that gets started when the thread is invoked
        """
        NUM_PACKETS_TO_FLUSH = 5
        # While the flag is not set, commence the regular operation of sniffing the packets
        while not self.restore_flag.is_set():
            for packet in self.capture:
                if len(self.session_information.packets) >= NUM_PACKETS_TO_FLUSH:
                    self.session_information.write_to_file()
                if 'IP' in packet and ((hasattr(packet.ip, "dst") and packet.ip.dst == self.target_ip) or (hasattr(packet.ip, "src") and packet.ip.src == self.target_ip)):
                    print("Packet acquired")

                    srcip = "None"
                    dstip = "None"
                    inbound_traffic = False
                    incoming_bytes = 0
                    outgoing_bytes = 0

                    if hasattr(packet.ip, "dst"):
                        if(packet.ip.dst == self.target_ip):
                            inbound_traffic = True
                        dstip = packet.ip.dst
                    if hasattr(packet.ip, "src"):
                        srcip = packet.ip.src

                    if 'UDP' in packet:
                        if inbound_traffic:
                            incoming_bytes = packet.udp.length

                        self.session_information.add_packet_info(
                            timestamp=round(time.time()), 
                                incoming_bytes=incoming_bytes, 
                                outgoing_bytes=outgoing_bytes,
                                srcport=packet.udp.srcport, 
                                dstport=packet.udp.dstport, 
                                transfer_protocol="None", 
                                connection_protocol="UDP", 
                                srcip=srcip, 
                                dstip=dstip)

                    if 'TCP' in packet:
                        transfer_protocol_type = "None"
                        if 'HTTP' in packet:
                            transfer_protocol_type = "HTTP"
                        elif 'TLS' in packet:
                            transfer_protocol_type = "HTTPS"
                        total_payload = 0

                        if hasattr(packet.tcp, "segment_data"):
                            if inbound_traffic:
                                incoming_bytes = len(packet.tcp.segment_data)
                            else:
                                outgoing_bytes = len(packet.tcp.segment_data)

                        self.session_information.add_packet_info(
                            timestamp=round(time.time()), 
                                incoming_bytes=incoming_bytes, 
                                outgoing_bytes=outgoing_bytes, 
                                srcport=packet.tcp.srcport, 
                                dstport=packet.tcp.dstport, 
                                transfer_protocol=transfer_protocol_type, 
                                connection_protocol="TCP", 
                                srcip=srcip, 
                                dstip=dstip)

        # If the flag is set (ie. the user has pressed ctrl+c), then close the capture gracefully
        print("\nClosing the pyshark capture ...")
        self.session_information.write_to_file()
        self.capture.close()


class SessionInformation:
    def __init__(self, output_file_name):
        """
        Default empty constructor that initializes the list of packets

        @param output_file_name         The output file name for the csv
        """
        self.packets = []
        self.output_file_name = output_file_name

    def add_packet_info(self, timestamp, incoming_bytes, outgoing_bytes, srcport, dstport, transfer_protocol, connection_protocol, srcip, dstip):
        """
        Adds the information to the list of packets

        @param  timestamp               The current timestamp of the packet

        @param  incoming_bytes          The incoming bytes for packet

        @param  outgoing_bytes          The outgoing bytes for packet

        @param  srcport                 The source port of the packet

        @param  dstport                 The destination port of the packet

        @param  transfer_protocol       The transfer protocol (HTTP or HTTPS or None)

        @param  connection_protocol     The connection protocol (UDP or TCP)

        @param  srcip                   The source IP address

        @param  dstip                   The destination IP address
        """
        self.packets.append((timestamp, incoming_bytes, outgoing_bytes, srcport,
                             dstport, transfer_protocol, connection_protocol, srcip, dstip))

    def write_to_file(self):
        """
        Writes the packet information to an output file in csv format.

        Clears out the buffer at the end, allowing the LiveCapture object to buffer up
        any incoming packets on its end.
        """

        print(
            f"Writing {len(self.packets)} packets to {self.output_file_name}")

        with open(self.output_file_name, 'a+', os.O_NONBLOCK) as output_file:
            writer = csv.writer(output_file)
            for row in self.packets:
                writer.writerow(row)

        output_file.close()

        # Clear out the packets as they have been written already
        self.packets = []
