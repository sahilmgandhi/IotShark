import requests
import sys
import csv
import json


class StaticCSVAnalysis():
    """
    This class performs some static analysis from the CSV data such as finding out
    the source/destination ISPs, the number of local connections, total bytes, ports,
    and other interesting statistics.
    """

    def __init__(self, csv_file):
        """
        Constructor

        @param  csv_file        The csv file to analyze
        """

        data = {}
        src_port_map = {}
        dst_port_map = {}
        isp_map = {}
        src_ip_map = {}
        dst_ip_map = {}
        tcp_map = {}
        tcp_map['incoming_bytes'] = 0
        tcp_map['outgoing_bytes'] = 0
        udp_map = {}
        udp_map['incoming_bytes'] = 0
        udp_map['outgoing_bytes'] = 0
        transfer_protocol_map = {}
        connection_protocol_map = {}
        num_local_connections = 0
        total_incoming_bytes = 0
        total_outgoing_bytes = 0

        with open(csv_file, 'r') as csv_data_file:
            csv_reader = csv.reader(csv_data_file)
            row_count = 0

            for row in csv_reader:
                print(f"Analyzing row {row_count}")
                row_count += 1

                curr_incoming_bytes = int(row[1])
                curr_outgoing_bytes = int(row[2])

                # Update the number of local connections
                if row[7][0:7] == "192.168" and row[8][0:7] == "192.168":
                    num_local_connections += 1

                # Update the total number of bytes
                total_incoming_bytes += curr_incoming_bytes
                total_outgoing_bytes += curr_outgoing_bytes

                # Update the bytes for the transfer protocol
                if row[5] in transfer_protocol_map:
                    transfer_protocol_map[row[5]
                                          ]['incoming_bytes'] += curr_incoming_bytes
                    transfer_protocol_map[row[5]
                                          ]['outgoing_bytes'] += curr_outgoing_bytes
                else:
                    transfer_protocol_map[row[5]] = {}
                    transfer_protocol_map[row[5]
                                          ]['incoming_bytes'] = curr_incoming_bytes
                    transfer_protocol_map[row[5]
                                          ]['outgoing_bytes'] = curr_outgoing_bytes

                # Update the bytes for the connection protocol
                if row[6] in connection_protocol_map:
                    connection_protocol_map[row[6]
                                            ]['incoming_bytes'] += curr_incoming_bytes
                    connection_protocol_map[row[6]
                                            ]['outgoing_bytes'] += curr_outgoing_bytes
                else:
                    connection_protocol_map[row[6]] = {}
                    connection_protocol_map[row[6]
                                            ]['incoming_bytes'] = curr_incoming_bytes
                    connection_protocol_map[row[6]
                                            ]['outgoing_bytes'] = curr_outgoing_bytes

                # Update the source port map
                if row[3] in src_port_map:
                    src_port_map[row[3]
                                 ]['outgoing_bytes'] += curr_outgoing_bytes
                else:
                    src_port_map[row[3]] = {}
                    src_port_map[row[3]
                                 ]['outgoing_bytes'] = curr_outgoing_bytes

                # Update the destination port map
                if row[4] in dst_port_map:
                    dst_port_map[row[4]
                                 ]['incoming_bytes'] += curr_incoming_bytes
                else:
                    dst_port_map[row[4]] = {}
                    dst_port_map[row[4]
                                 ]['incoming_bytes'] = curr_incoming_bytes

                # Update the source ip map
                if row[8] in src_ip_map:
                    src_ip_map[row[8]]['outgoing_bytes'] += curr_outgoing_bytes
                else:
                    src_ip_map[row[8]] = {}
                    src_ip_map[row[8]]['outgoing_bytes'] = curr_outgoing_bytes

                # Update the destination ip map
                if row[7] in dst_ip_map:
                    dst_ip_map[row[7]]['incoming_bytes'] += curr_incoming_bytes
                else:
                    dst_ip_map[row[7]] = {}
                    dst_ip_map[row[7]]['incoming_bytes'] = curr_incoming_bytes

                # Update the isp map for source IP
                if row[7] in isp_map or row[7][0:7] == "192.168":
                    print(
                        'Source IP is either in map or local IP address. Skipping ...')
                else:
                    try:
                        req_string = 'http://ip-api.com/json/' + str(row[7])
                        r = requests.get(req_string).json()
                        if 'isp' in r:
                            isp_map[row[7]] = r['isp']
                    except Exception as e:
                        print("Could not download json" + str(e))

                # Update the isp map for destination IP
                if row[8] in isp_map or row[8][0:7] == "192.168":
                    print(
                        'Desination IP is either in map or local IP address. Skipping ...')
                else:
                    try:
                        req_string = 'http://ip-api.com/json/' + str(row[8])
                        r = requests.get(req_string).json()
                        if 'isp' in r:
                            isp_map[row[8]] = r['isp']
                    except Exception as e:
                        print("Could not download json" + str(e))

                # Update the tcp or udp maps
                if row[6] == "UDP":
                    udp_map['incoming_bytes'] += curr_incoming_bytes
                    udp_map['outgoing_bytes'] += curr_outgoing_bytes

                if row[6] == "TCP":
                    tcp_map['incoming_bytes'] += curr_incoming_bytes
                    tcp_map['outgoing_bytes'] += curr_outgoing_bytes

        json_file = csv_file[:-4] + ".json"

        data['total_incoming_bytes'] = total_incoming_bytes
        data['total_outgoing_bytes'] = total_outgoing_bytes
        data['total_bytes'] = total_incoming_bytes + total_outgoing_bytes
        data['num_local_connections'] = num_local_connections
        data['num_global_connections'] = row_count - num_local_connections
        data['num_total_connections'] = row_count
        data['src_port_map'] = src_port_map
        data['dst_port_map'] = dst_port_map
        data['protocol_map'] = transfer_protocol_map
        data['connection_map'] = connection_protocol_map
        data['isp_map'] = isp_map
        data['src_ip_map'] = src_ip_map
        data['dst_ip_map'] = dst_ip_map
        data['udp_map'] = udp_map
        data['tcp_map'] = tcp_map

        with open(json_file, 'w') as output_file:
            json.dump(data, output_file, indent=4)


if __name__ == "__main__":
    csv_file = ""

    if len(sys.argv) == 1:
        print("Input file is required. Exiting now ...")
        sys.exit(0)
    else:
        csv_file = sys.argv[1]

    StaticCSVAnalysis(csv_file=csv_file)
