#!/usr/bin/env python3
# -.- coding: utf-8 -.-

import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

import os
import sys
import time
import json
import sqlite3
import datetime
import argparse
import threading
from scapy.all import *
import urllib.request as urllib2

parser = argparse.ArgumentParser(
    usage="probeSniffer.py interface [-h] [-d] [-b] [--nosql] [--addnicks] [--flushnicks] [--debug]")
parser.add_argument(
    "interface", help='interface (in monitor mode) for capturing the packets')
parser.add_argument("-d", action='store_true',
                    help='do not show duplicate requests')
parser.add_argument("-b", action='store_true',
                    help='do not show \'broadcast\' requests (without ssid)')
parser.add_argument("-a", action='store_true',
                    help='save duplicate requests to SQL')
parser.add_argument(
    "-f", type=str, help='only show requests from the specified mac address')
parser.add_argument('-r', '--rssi', action='store_true',
                    help="include rssi in output")
parser.add_argument("--nosql", action='store_true',
                    help='disable SQL logging completely')
parser.add_argument("--addnicks", action='store_true',
                    help='add nicknames to mac addresses')
parser.add_argument("--flushnicks", action='store_true',
                    help='flush nickname database')
parser.add_argument('--noresolve', action='store_true',
                    help="skip resolving mac address")
parser.add_argument("--debug", action='store_true', help='turn debug mode on')

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)
args = parser.parse_args()
showDuplicates = not args.d
showBroadcasts = not args.b
noSQL = args.nosql
addNicks = args.addnicks
flushNicks = args.flushnicks
debugMode = args.debug
saveDuplicates = args.a
filterMode = args.f != None
rssi = args.rssi
noresolve = args.noresolve
if args.f != None:
    filterMac = args.f

monitor_iface = args.interface
alreadyStopping = False


def restart_line():
    sys.stdout.write('\r')
    sys.stdout.flush()


def statusWidget(devices):
    sys.stdout.write("Devices found: [" + str(devices) + "]")
    restart_line()
    sys.stdout.flush()


header = """
 ____  ____   ___  ____    ___ _________  ____ _____ _____  ___ ____
|    \|    \ /   \|    \  /  _/ ___|    \|    |     |     |/  _|    \\
|  o  |  D  |     |  o  )/  [(   \_|  _  ||  ||   __|   __/  [_|  D  )
|   _/|    /|  O  |     |    _\__  |  |  ||  ||  |_ |  |_|    _|    /
|  |  |    \|     |  O  |   [_/  \ |  |  ||  ||   _]|   _|   [_|    \\
|  |  |  .  |     |     |     \    |  |  ||  ||  |  |  | |     |  .  \\
|__|  |__|\_|\___/|_____|_____|\___|__|__|____|__|  |__| |_____|__|\__|
"""

try:
    print(header + "                                       v2.1 by David Schütz (@xdavidhu)\n")
except:
    print(header + "                                                      v2.1 by @xdavidhu\n")

print("[W] Make sure to use an interface in monitor mode!\n")

devices = []
script_path = os.path.dirname(os.path.realpath(__file__))
script_path = script_path + "/"

print("[I] Loading MAC database...")
with open(script_path + "oui.json", 'r') as content_file:
    obj = content_file.read()
resolveObj = json.loads(obj)

externalOptionsSet = False
if noSQL:
    externalOptionsSet = True
    print("[I] NO-SQL MODE!")
if  not showDuplicates:
    externalOptionsSet = True
    print("[I] Not showing duplicates...")
if not showBroadcasts:
    externalOptionsSet = True
    print("[I] Not showing broadcasts...")
if filterMode:
    externalOptionsSet = True
    print("[I] Only showing requests from '" + filterMac + "'.")
if saveDuplicates:
    externalOptionsSet = True
    print("[I] Saving duplicates to SQL...")
if externalOptionsSet:
    print()

PROBE_REQUEST_TYPE = 0
PROBE_REQUEST_SUBTYPE = 4

if not noSQL:
    # nosql
    pass


def stop():
    global alreadyStopping
    debug("stoping called")
    if not alreadyStopping:
        debug("setting stopping to true")
        alreadyStopping = True
        print("\n[I] Stopping...")
        if not noSQL:
            print("[I] Results saved to 'DB-probeSniffer.db'")
        print("\n[I] probeSniffer stopped.")
        return


def debug(msg):
    if debugMode:
        print("[DEBUG] " + msg)


def chopping():
    while True:
        if not alreadyStopping:
            channels = [1, 6, 11]
            for channel in channels:
                os.system("iwconfig " + monitor_iface + " channel " +
                          str(channel) + " > /dev/null 2>&1")
                debug("[CHOPPER] HI IM RUNNING THIS COMMAND: " +
                      "iwconfig " + monitor_iface + " channel " + str(channel))
                debug("[CHOPPER] HI I CHANGED CHANNEL TO " + str(channel))
                time.sleep(5)
        else:
            debug("[CHOPPER] IM STOPPING TOO")
            sys.exit()


def sniffer():
    global alreadyStopping
    while True:
        if not alreadyStopping:
            try:
                debug("[SNIFFER] HI I STARTED TO SNIFF")
                sniff(iface=monitor_iface, prn=PacketHandler, store=0)
            except:
                print("[!] An error occurred. Debug:")
                print(traceback.format_exc())
                print("[!] Restarting in 5 sec... Press CTRL + C to stop.")
                time.sleep(5)
        else:
            debug("[SNIFFER] IM STOPPING TOO")
            sys.exit()

def resolveMac(mac):
    try:
        global resolveObj
        for macArray in resolveObj:
            if macArray[0] == mac[:8].upper():
                return macArray[1]
        return "RESOLVE-ERROR"
    except:
        return "RESOLVE-ERROR"

def PacketHandler(pkt):
    try:
        debug("packethandler - called")
        if pkt.haslayer(Dot11):
            debug("packethandler - pkt.haslayer(Dot11)")
            if pkt.type == PROBE_REQUEST_TYPE and pkt.subtype == PROBE_REQUEST_SUBTYPE:
                debug("packethandler - if pkt.type")
                PrintPacket(pkt)
                debug("packethandler - printPacket called and done")
    except KeyboardInterrupt:
        debug("packethandler - keyboardinterrupt")
        stop()
        exit()
    except:
        debug("packethandler - exception")
        stop()
        exit()

def PrintPacket(pkt):
    statusWidget(len(devices))
    debug("printpacket started")
    ssid = pkt.getlayer(Dot11ProbeReq).info.decode("utf-8")
    rssi_val = None
    if rssi:
        rssi_val = -(256 - ord(pkt.notdecoded[-2:-1]))
        debug("rssi value: " + str(rssi_val))
    if ssid == "":
        nossid = True
        debug("no ssid in request... skipping")
        debug(str(pkt.addr2) + " " + str(pkt.addr1))
    else:
        nossid = False
    print_source = pkt.addr2
    mac_address = print_source
    if not noresolve:
        debug("resolving mac")
        vendor = resolveMac(mac_address)
        debug("vendor query done")
    else:
        vendor = "RESOLVE-OFF"
    inDevices = False
    for device in devices:
        if device == mac_address:
            inDevices = True
    if not inDevices:
        devices.append(mac_address)
    nickname = getNickname(print_source)
    if filterMode:
        if mac_address != filterMac:
            return
    if not nossid:
        try:
            debug("sql duplicate check started")
            if not noSQL:
                if not checkSQLDuplicate(ssid, mac_address):
                    debug("not duplicate")
                    debug("saving to sql")
                    saveToMYSQL(mac_address, vendor, ssid, rssi_val)
                    debug("saved to sql")
                    if not noresolve:
                        print(print_source + (" [" + str(nickname) + "]" if nickname else "") + " (" + vendor + ")" + (" [" + str(rssi_val) + "]" if rssi_val else "") +  " ==> '" + ssid + "'")
                    else:
                        print(print_source + (" [" + str(nickname) + "]" if nickname else "") + (" [" + str(rssi_val) + "]" if rssi_val else "") +  " ==> '" + ssid + "'")
                else:
                    if saveDuplicates:
                        debug("saveDuplicates on")
                        debug("saving to sql")
                        saveToMYSQL(mac_address, vendor, ssid, rssi_val)
                        debug("saved to sql")
                    if showDuplicates:
                        debug("duplicate")
                        if not noresolve:
                            print("[D] " + print_source + (" [" + str(nickname) + "]" if nickname else "") + " (" + vendor + ")" + (" [" + str(rssi_val) + "]" if rssi_val else "")  + " ==> '" + ssid + "'")
                        else:
                            print("[D] " + print_source + (" [" + str(nickname) + "]" if nickname else "") + (" [" + str(rssi_val) + "]" if rssi_val else "")  + " ==> '" + ssid + "'")
            else:
                if not noresolve:
                    print(print_source + (" [" + str(nickname) + "]" if nickname else "") + " (" + vendor + ")" + (" [" + str(rssi_val) + "]" if rssi_val else "") + " ==> '" + ssid + "'")
                else:
                    print(print_source + (" [" + str(nickname) + "]" if nickname else "") + (" [" + str(rssi_val) + "]" if rssi_val else "") + " ==> '" + ssid + "'")
        except KeyboardInterrupt:
            stop()
            exit()
        except:
            pass
    else:
        if showBroadcasts:
            if not noresolve:
                print(print_source + (" [" + str(nickname) + "]" if nickname else "") + " (" + vendor + ")" + (" [" + str(rssi_val) + "]" if rssi_val else "") + " ==> BROADCAST")
            else:
                print(print_source + (" [" + str(nickname) + "]" if nickname else "") + (" [" + str(rssi_val) + "]" if rssi_val else "") + " ==> BROADCAST")
    statusWidget(len(devices))


def SQLConncetor():
    try:
        debug("sqlconnector called")
        global db
        db = sqlite3.connect("DB-probeSniffer.db")
        cursor = db.cursor()
        return cursor
    except KeyboardInterrupt:
        stop()
        exit()
    except:
        debug("[!!!] CRASH IN SQLConncetor")
        debug(traceback.format_exc())


def checkSQLDuplicate(ssid, mac_add):
    try:
        debug("[1] checkSQLDuplicate called")
        cursor = SQLConncetor()
        cursor.execute(
            "select count(*) from probeSniffer where ssid = ? and mac_address = ?", (ssid, mac_add))
        data = cursor.fetchall()
        data = str(data)
        debug("[2] checkSQLDuplicate data: " + str(data))
        db.close()
        return data != "[(0,)]"
    except KeyboardInterrupt:
        stop()
        exit()
    except:
        debug("[!!!] CRASH IN checkSQLDuplicate")
        debug(traceback.format_exc())


def saveToMYSQL(mac_add, vendor, ssid, rssi_in):
    try:
        debug("saveToMYSQL called")
        cursor = SQLConncetor()
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("INSERT INTO probeSniffer VALUES (?, ?, ?, ?,?)", (mac_add, vendor, ssid,  st, rssi_in))
        db.commit()
        db.close()
    except KeyboardInterrupt:
        stop()
        exit()
    except:
        debug("[!!!] CRASH IN saveToMYSQL")
        debug(traceback.format_exc())


def setNickname(mac, nickname):
    debug("setNickname called")
    cursor = SQLConncetor()
    cursor.execute(
        "INSERT INTO probeSnifferNicknames VALUES (?, ?)", (mac, nickname))
    db.commit()
    db.close()


def getNickname(mac):
    debug("getNickname called")
    cursor = SQLConncetor()
    cursor.execute(
        "SELECT nickname FROM probeSnifferNicknames WHERE mac = ?", (mac,))
    data = cursor.fetchone()
    db.close()
    if data == None:
        return False
    else:
        data = data[0]
        data = str(data)
        return data


def main():
    global alreadyStopping

    if not noSQL:
        print("[I] Setting up SQLite...")

        try:
            setupDB = sqlite3.connect("DB-probeSniffer.db")
        except:
            print("\n[!] Cant connect to database. Permission error?\n")
            exit()
        setupCursor = setupDB.cursor()
        if flushNicks:
            try:
                setupCursor.execute("DROP TABLE probeSnifferNicknames")
                print("\n[I] Nickname database flushed.\n")
            except:
                print(
                    "\n[!] Cant flush nickname database, since its not created yet\n")
        setupCursor.execute(
            "CREATE TABLE IF NOT EXISTS probeSniffer (mac_address VARCHAR(50),vendor VARCHAR(50),ssid VARCHAR(50), date VARCHAR(50), rssi INT)")
        setupCursor.execute(
            "CREATE TABLE IF NOT EXISTS probeSnifferNicknames (mac VARCHAR(50),nickname VARCHAR(50))")
        setupDB.commit()
        setupDB.close()

    if addNicks:
        print("\n[NICKNAMES] Add nicknames to mac addresses.")
        while True:
            print()
            mac = input("[?] Mac address: ")
            if mac == "":
                print("[!] Please enter a mac address.")
                continue
            nick = input("[?] Nickname for mac '" + str(mac) + "': ")
            if nick == "":
                print("[!] Please enter a nickname.")
                continue
            setNickname(mac, nick)
            addAnother = input("[?] Add another nickname? Y/n: ")
            if addAnother.lower() == "y" or addAnother == "":
                pass
            else:
                break

    print("[I] Starting channelhopper in a new thread...")
    path = os.path.realpath(__file__)
    chopper = threading.Thread(target=chopping)
    chopper.daemon = True
    chopper.start()
    print("[I] Saving requests to 'DB-probeSniffer.db'")
    print("\n[I] Sniffing started... Please wait for requests to show up...\n")
    statusWidget(len(devices))
    snifferthread = threading.Thread(target=sniffer)
    snifferthread.daemon = True
    snifferthread.start()
    try:
        while not alreadyStopping:
            pass
    except KeyboardInterrupt:
        alreadyStopping = True
        print("\n[I] Stopping...")
        if not noSQL:
            print("[I] Results saved to 'DB-probeSniffer.db'")
        print("\n[I] probeSniffer stopped.")
    except OSError:
        print("[!] An error occurred. Debug:")
        print(traceback.format_exc())
        print("[!] Restarting in 5 sec... Press CTRL + C to stop.")
        try:
            time.sleep(5)
        except:
            alreadyStopping = True
            print("\n[I] Stopping...")
            if not noSQL:
                print("[I] Results saved to 'DB-probeSniffer.db'")
            print("\n[I] probeSniffer stopped.")

    if not alreadyStopping:
        print("\n[I] Stopping...")
        if not noSQL:
            print("[I] Results saved to 'DB-probeSniffer.db'")
        print("\n[I] probeSniffer stopped.")


if __name__ == "__main__":
    main()
