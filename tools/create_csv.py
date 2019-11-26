# This file creates a csv file with dummy data for the grapher

import csv
import time
import random
import sys

transfer_protocols = ['HTTP', 'HTTPS']
connection_protocols = ['UDP', 'TCP']

if len(sys.argv) == 1:
    total_rows = 100
else:
    total_rows = int(sys.argv[1])

curr_time = round(time.time())
copy_time = curr_time
output_file = "../csv/dummycsv_192.168.1.10_" + str(curr_time) + ".csv"

while True:
    packets = []
    curr_time = round(time.time())
    copy_time = curr_time
    for i in range(0, total_rows):
        copy_time += random.randint(0, 4)
        packets.append((copy_time, random.randint(50, 500),
                        random.randint(1, 5), random.randint(6, 10), random.choice(transfer_protocols), random.choice(connection_protocols)))

    with open(output_file, 'a') as of:
        writer = csv.writer(of)
        for row in packets:
            writer.writerow(row)

    of.close()
    time.sleep(2)
