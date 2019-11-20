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

# Data File Format

The captured data is stored in a csv file with the following format:

{timestamp, port, type, bytes}

``` CSV
123123213, 80, HTTP, 200
123123240, 443, HTTPS, 3023
```