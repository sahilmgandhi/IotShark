from src.ArpSpoofing import ArpSpoofing
from src.DiscoverHosts import select_device
from src.PySharkCapture import PySharkCapture
from src.StaticCSVAnalysis import StaticCSVAnalysis
from src.UserState import UserState
from subprocess import call, PIPE
import argparse
import os
import signal
import sys
import time
import threading
from app import FlaskApp
import keyboard

"""
Use cases:
1. Specify the IP of target IoT device and the IP of the gateway router. The script skips scanning hosts and starts ARP poisoning
    sudo python iotshark.py -t 192.168.0.215 -g 192.168.0.1

2. Specify a subnet mask for host scanning and the IP of the gateway router. The script scans the given subnet, prompts the user to select a target device and starts ARP poisoning.
    sudo python iotshark.py -s 192.168.0.0/24 -g 192.168.0.1

3. Don't specify anything (like a regular user). The script scans common residential subnets and continues the same way as (2).
    sudo python iotshark.py

4. Specify the path to a csv containing captured data. The script will start the Flask server and output a graph of the data.
    python iotshark.py -f csv/packetdump_192.168.1.13_1574744945.csv
"""


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target",
                        help="Target IP")
    parser.add_argument("-f", "--file", dest="file",
                        help="CSV file containing captured data")
    parser.add_argument("-u", "--userstate", dest="userstate",
                        help="User State file containing user's interaction with the IoT device")
    parser.add_argument("-g", "--gateway", dest="gateway",
                        help="Gateway IP")
    parser.add_argument("-s", "--scan", dest="scan",
                        help="Subnet mask for scanning hosts")
    options = parser.parse_args()
    return options


def cleanup():
    """
    Clean up and exit the script after user issues SIGTERM
    """
    # Close the flask app
    flask_app.restore_flag.set()

    # Close the pyshark capture
    pyshark_capture.restore_flag.set()
    pyshark_capture.join()

    # Restore the ARP Spoofing tables
    arp_spoofing.restore_flag.set()
    arp_spoofing.join()

    print("Performing static analysis on CSV file now ... ")
    file_name = 'csv/packetdump_' + target + '_' + timestamp + '.csv'
    StaticCSVAnalysis(csv_file=file_name)

    print("Static analysis finished. Press Ctrl+C again to stop the Flask Server ...")

    sys.exit(0)


options = get_arguments()
if options.file:
    flask_app = FlaskApp(target_file=options.file, userstate_file=options.userstate,
                         target_ip=None, file_timestamp=None)
    flask_app.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        # Close the flask app
        flask_app.restore_flag.set()
        sys.exit(0)
else:
    if os.geteuid() != 0:
        print("Root privilege is needed to discover hosts using nmap.")
        sys.exit(1)

    target, gateway = select_device(options)

    arp_spoofing = ArpSpoofing(target, gateway)
    arp_spoofing.start()

    timestamp = str(round(time.time()))
    pyshark_capture = PySharkCapture(target, timestamp)
    pyshark_capture.start()
    user_state = UserState(target, timestamp)

    flask_app = FlaskApp(target_file=None, userstate_file=None,
                         target_ip=target, file_timestamp=timestamp)
    flask_app.start()

    try:
        # a Unix epoch for the last time the "user speaking button" is pressed
        speaking_button_debouncing = None
        while True:
            # User can press Space to log his interaction with the voice assistant.
            # Ex. press Space once and begin speaking to Alexa; press it again after finish speaking
            # Assume adjacent presses of the key is at least 1 second away to debounce keyboard key press check
            if speaking_button_debouncing is not None and time.time() < speaking_button_debouncing + 1:
                continue
            if keyboard.is_pressed('space'):
                user_state.toggle_user_speaking_state()
                speaking_button_debouncing = time.time()
            elif keyboard.is_pressed('ctrl+c'):
                print(" User pressed Ctrl-C.")
                cleanup()

    except KeyboardInterrupt:
        cleanup()
