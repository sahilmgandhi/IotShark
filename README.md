# cs219-f19-final-project
# DASH: Determine And Secure the House

This is our final project for CS 219 for the Fall 2019 quarter. 

DASH is a IOT monitoring service that allows users to monitor their IOT devices for trends in data sent/received.
Ordinarily, setting up a man in the middle attack with proper configurations can take up quite a bit of time, and 
may seem dauntingly impossible for those with little to no experience in computer security or even computer science.

DASH aims to provide a [nearly] fully automated solution for a user to monitor their IOT devices by simply running 
a single script. The user merely has to select which device they wish to monitor, and this program takes care of the 
rest of the heavy work by starting the ARP poisoning, setting up the packet forwarding and the man in the middle 
packet sniffer. It also has an easy to understand and interactive web UI where a user can filter the packets based on 
the ports, types, and timestamps to get a broader understanding of how much and when things are being transmitted.

We also aim to classify certain kinds of data such as heartbeat messages, data transfers, and anomalies, though the 
last one will likely be demonstrated on the un-encrypted RPi test since it is difficult to do anomaly detection without
huge amounts of data (and we would require many devices and individuals to gather that much data). 

# TODOs

1. Combine the three services together
2. Test on other devices to automate some more of the setup
3. Test on a R-Pi for non-encrypted data.
4. Finish this README

# How to run;

1. Install the required libraries `$pip3 -r requirements.txt`
2. `$sudo sysctl net.inet.ip.forwarding=1`
3. ... TODO:

## The Main Script
Create a Python virtual envionment and install dependency packages.

```sh
virtualenv --python=`which python3` venv
source venv/bin/activate
python -r requirements.txt
```

Make sure packet forwarding is enabled on your local machine. This is necessary for man-in-the-middle attack to work. On macOS this can be done with:

```sh
sudo sysctl net.inet.ip.forwarding=1
```

Run the main program `mitm_main.py`. See that script for accepted options.

Currently this program does three things:
1. Scan for all hosts either in the given subnet by the `-s` option or a set of common residential subnets
2. Discover the hardware vendor and OS of each host
3. Perform ARP poisoning between the selected host and gateway router

After ARP poisoning is running, you can examine traffic from the target device by Wireshark with a display filter like: 

```
(ip.src==192.168.0.215 or ip.dst==192.168.0.215) and tcp.port != 443
```

# Data File Format

The captured data is stored in a csv file with the following format:

{timestamp, bytes, srcport, dstport, transfer_protocol, connection_protocol}

``` CSV
123123213, 36, 80, 65124, HTTP, UDP
123123240, 800, 443, 65125, HTTPS, TCP
```

# Using the Tool to Sniff IoT Devices

For example, here is a long string that we can say to Alexa Echo Dot/Google Home while sniffing their traffic. Pay attention if the device is transmitting data before the wake word.

```
It is a dark and stormy night. My friends and I just came back from the Yosemite National Park, where the quick brown fox jumps over the lazy dog. Next week is Thanksgiving. Black Friday in 2019 is coming as well. It's a good time to do something exciting, such as taking a Computer Security class or a Programming Language class at UCLA. By the way, the first Airbus A380 jumbo jet is retiring. We like flying in that plane.

WAKE_WORD, what is the weather like in Los Angeles on Thanksgiving?

Anyways, we have Boeing 787 Dreamliners for cross-continental flights. The Web and Mobile System class with Ravi is amazing. We should upgrade the commercial laundry machine during the Black Friday sale. The bright and sunny weather is coming back and a trip to Joshua Tree National Park awaits. Well, I just saw a slow cat crashed into a new Android robot. There are some other robots made by Apple and Amazon too.
```
