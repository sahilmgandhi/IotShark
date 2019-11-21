import pyshark
import csv
import threading
import time


class PySharkCapture(threading.Thread):
    def __init__(self, target_ip):
        """
        Constructor

        @param  target_ip       The target IP address to intercept
        """
        threading.Thread.__init__(self)
        self.restore_flag = threading.Event()

        self.target_ip = target_ip
        self.output_file_name = "packetdump" + \
            str(target_ip) + str(round(time.time())) + ".csv"

        self.session_information = SessionInformation()

    def run(self):
        """
        Entrypoint that gets started when the thread is invoked
        """

        # Start capturing data
        capture = pyshark.LiveCapture(interface='en0')
        capture.set_debug()
        capture.sniff(timeout=5)

        # While the flag is not set, commence the regular operation of sniffing the packets
        while not self.restore_flag.is_set():
            for packet in capture:
                print("1")

        # If the flag is set (ie. the user has pressed ctrl+c), then close the capture gracefully
        print("\nClosing the pyshark capture ...")
        capture.close()


class SessionInformation:
    def __init(self):
        """
        Default empty constructor that initializes the list of packets
        """
        self.packets = []

    def add_packet_info(self, timestamp, total_bytes, srcport, dstport, transfer_protocol, connection_protocol):
        """
        Adds the information to the list of packets

        @param  timestamp               The current timestamp of the packet

        @param  total_bytes             The total payload size of packet in bytes

        @param  srcport                 The source port of the packet

        @param  dstport                 The destination port of the packet

        @param  transfer_protocol       The transfer protocol (HTTP or HTTPS)

        @param  connection_protocol     The connection protocol (UDP or TCP)
        """
        self.packets.append((timestamp, total_bytes, srcport,
                             dstport, transfer_protocol, connection_protocol))

    def write_to_file(self):
        """
        Writes the packet information to an output file in csv format.

        Clears out the buffer at the end, allowing the LiveCapture object to buffer up
        any incoming packets on its end.
        """

        with open(output_file_name, 'a') as output_file:
            writer = csv.writer(output_file)
            for row in self.packets:
                writer.writerow(row)

        output_file.close()

        # Clear out the packets as they have been written already
        self.packets = []
