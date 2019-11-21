# This is just a testing file for a playground, NOT to be used in the actual tool

import pyshark
import csv

"""
Global variables

TODO: Make filename random or based on timestamp + device or user defined
TODO: Make the IP address automatically generated through the scapy part
"""
output_file_name = "packetdump.csv"
device_ip_address = "192.168.0.215"
out_string = ""
i = 0


class SessionInformation:
    def __init(self):
        """
        Default empty constructor that initializes the list of packets
        """
        self.packets = []

    def add_packet_info(self, timestamp, port, packet_type, total_bytes):
        """
        Adds the information to the list of packets

        @param  timestamp       The current timestamp of the packet

        @param  port            The port of the packet

        @param  packet_type     The type of the packet (eg. HTTP, HTTPS)

        @param  total_bytes     The total payload size of packet in bytes
        """
        self.packets.append((timestamp, port, packet_type, total_bytes))

    def write_to_file(self):
        """
        Writes the packet information to an output file in csv format.

        Clears out the buffer at the end, allowing the LiveCapture object to buffer up
        any incoming packets on its end.
        """
        global output_file_name
        with open(output_file_name, 'a') as output_file:
            writer = csv.writer(output_file)
            for row in self.packets:
                writer.writerow(row)

        output_file.close()

        # Clear out the packets as they have been written already
        self.packets = []


# Start capturing data
capture = pyshark.LiveCapture(
    interface='en0')  # , include_raw=True, use_json=True)
capture.set_debug()
capture.sniff(timeout=5)

for packet in capture:
    # print(captures.ip.field_names)
    # if 'IP' in packet and 'TCP' in packet and 'HTTP' in packet:
    #     if packet.ip.dst == device_ip_address or packet.ip.src == device_ip_address:
    print(i)
    i += 1
    # print(bytearray.fromhex(packet.tcp.payload).decode())
    # print('The src port is ' + packet.tcp.srcport)
    # print('The dest port is ' + packet.tcp.dstport)
    # print("The payload is : " + str(packet.http))

    # if packet.tcp.srcport == 80 or packet.tcp.dstport == 80:
    # print(packet.tcp.data)

    out_file = open("Eavesdrop_Data.txt", "w")
    out_string += "Packet #         " + str(i)
    out_string += "\n"
    out_string += str(packet)
    out_string += "\n"
    out_file.write(out_string)

    """
    if 'TCP' in packet:
        # if hasattr(packet.tcp, "payload"):
        #     print(packet.tcp.payload)
        if hasattr(packet.tcp, "segment_data"):
            print("Segment data is " + packet.tcp.segment_data)
            print(
                f"Segment data size in bytes is {len(packet.tcp.segment_data)}")

        # payload, time_relative, time_delta, srcport, port, dstport, options, option_len
        # segment_data, window_size, window_size_value, len, analysis_push_bytes_sent
        # hdr_len, options_timestamp
    """
    if 'UDP' in packet:
        print("UDP received")
        print(dir(packet.udp))

        """
            layer_name, port, dstport, srcport,
            length, time_delta, 
        """

capture.close()
