
     ____  ____   ___  ____    ___ _________  ____ _____ _____  ___ ____    
    |    \|    \ /   \|    \  /  _/ ___|    \|    |     |     |/  _|    \   
    |  o  |  D  |     |  o  )/  [(   \_|  _  ||  ||   __|   __/  [_|  D  )  
    |   _/|    /|  O  |     |    _\__  |  |  ||  ||  |_ |  |_|    _|    /   
    |  |  |    \|     |  O  |   [_/  \ |  |  ||  ||   _]|   _|   [_|    \   
    |  |  |  .  |     |     |     \    |  |  ||  ||  |  |  | |     |  .  \  
    |__|  |__|\_|\___/|_____|_____|\___|__|__|____|__|  |__| |_____|__|\__|
                                           v3.0 by David Schütz (@xdavidhu)
[![Build Status](https://travis-ci.org/xdavidhu/probeSniffer.svg?branch=master)](https://travis-ci.org/xdavidhu/probeSniffer)
[![Compatibility](https://img.shields.io/badge/python-3.3%2C%203.4%2C%203.5%2C%203.6-brightgreen.svg)](https://github.com/xdavidhu/probeSniffer)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/xdavidhu/probeSniffer/blob/master/LICENSE)
[![Stars](https://img.shields.io/github/stars/xdavidhu/probeSniffer.svg)](https://github.com/xdavidhu/probeSniffer)

### ⚠️ Warning! This project is no longer maintained and may not work as expected.

<h3>A tool for sniffing unencrypted wireless probe requests from devices</h3>

# New in version 3.0
  * Less packet drop<br>
  * Offline / Faster vendor resolving<br>
  * Way better performance on slower systems<br>
  * Switched from scapy library to tshark packet capture<br>
  * Displaying / Logging BSSID's from probe requests (only if not broadcast)<br>

# Features
  * Capturing and displaying probe requests in real time<br>
  * Offline vendor resolving from MAC addresses<br>
  * Displaying the number of devices nearby<br>
  * Displaying the RSSIs of probe requests<br>
  * Option to seck nicknames for MAC addresses<br>
  * Option to filter output by MAC address<br>
  * Displaying BSSIDs from probe requests<br>
  * Capturing "broadcast" probe requests (without SSID)<br>
  * Logging the probe requests to an SQLite database file<br>

# Requirements
  * Kali Linux / Raspberry Pi OS with root privileges<br>
  * Python3, pip3, tshark and pyshark<br>
  * A wireless adapter capable of monitor mode<br>

# Options
  * <b>-h</b> / display the help message<br>
  * <b>-d</b> / do not show duplicate requests<br>
  * <b>-b</b> / do not show "broadcast" requests (without SSID)<br>
  * <b>-a</b> / save duplicate requests to SQL<br>
  * <b>--filter</b> / only show requests from the specified MAC address<br>
  * <b>--norssi</b> / do not include RSSI in output<br>
  * <b>--nosql</b> / disable SQL logging completely<br>
  * <b>--addnicks</b> / add nicknames to mac addresses<br>
  * <b>--flushnicks</b> / flush nickname database<br>
  * <b>--noresolve</b> / skip resolving mac address<br>
  * <b>--debug</b> / turn debug mode on<br>

# Installing
<h3>Kali Linux / Raspberry Pi OS</h3>

```
$ sudo apt-get update && sudo apt-get install git python3 python3-pip tshark -y

$ git clone https://github.com/xdavidhu/probeSniffer

$ cd probeSniffer

$ python3 -m pip install -r requirements.txt
```

**WARNING**: probeSniffer is only compatible with Python 3.3, 3.4, 3.5 and 3.6.

# Usage
**Make sure to put your interface into monitor mode!**</br>
You can use airmon-ng to do this:

```
$ sudo airmon-ng start [interface]
```

If the command above doesn't work for you, try this:
```
$ sudo ip link set [interface] down
$ sudo iw dev [interface] set type monitor
```

Finally, run the script:
```
$ sudo python3 probeSniffer.py [interface] [options]
```

# Disclaimer
I'm not responsible for anything you do with this program, so please only use it for good and educational purposes.
