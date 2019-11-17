import pyshark

capture = pyshark.LiveCapture(
    interface='en0')
capture.set_debug()
capture.sniff(timeout=5)

out_string = ""

i = 0
for packet in capture:
    # print(captures.ip.field_names)
    if 'IP' in packet and 'TCP' in packet and 'HTTP' in packet:
        if packet.ip.dst == "192.168.0.215" or packet.ip.src == "192.168.0.215":
            print(i)
            i += 1
            # print(bytearray.fromhex(packet.tcp.payload).decode())
            print('The src port is ' + packet.tcp.srcport)
            print('The dest port is ' + packet.tcp.dstport)
            print("The payload is : " + str(packet.http))

            # if packet.tcp.srcport == 80 or packet.tcp.dstport == 80:
            # print(packet.tcp.data)

        # out_file = open("Eavesdrop_Data.txt", "w")
        # out_string += "Packet #         " + str(i)
        # out_string += "\n"
        # out_string += str(packet)
        # out_string += "\n"
        # out_file.write(out_string)
# for packet in capture.sniff_continuously(packet_count=5):
#     print('Just arrived:', packet)

capture.close()
