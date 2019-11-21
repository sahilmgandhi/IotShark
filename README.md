# cs219-f19-final-project
## Environment Setup
Create a Python virtual envionment and install dependency packages.

```sh
virtualenv --python=`which python3` venv
source venv/bin/activate
python -r requirements.txt
```

## Run the Script
First, make sure packet forwarding is enabled on your local machine. This is necessary for man-in-the-middle attack to work. On macOS this can be done with:

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
