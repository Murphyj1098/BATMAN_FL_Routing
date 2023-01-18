#!/usr/bin/python3

import argparse
import os
from emane.events import EventService, LocationEvent, PathlossEvent
import subprocess

def getOGMTable():
    ogmTable = "batctl o"
    proc_out = subprocess.run(args=ogmTable, shell=True, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    table_list = proc_out.stdout.split("\n")
    table_list = table_list[2:]
    return table_list


def sendPathLossEvent(nemIDSrc, nemIDDest, pathlossTo, pathlossFrom=0, sym=True):
    if sym == True:
        pathlossFrom = pathlossTo
    
    event = PathlossEvent()
    event.append(nemId=nemIDDest, forward=pathlossTo, reverse=pathlossFrom)
    EMANEEventChannel.publish(nemIDSrc, event)

    
def sendLocationEvent(nemID, lat, lon, altitude=0):
    event = LocationEvent()
    event.append(nemID, latitude=lat, longitude=lon, altitude=altitude)
    EMANEEventChannel.publish(0, event)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A tool to retrive the transmission quality metric from the B.A.T.M.A.N. routing algorithm.")
    parser.add_argument('--time', '-t', action='store', type=float, nargs='?', default=1, help='Number of seconds between OGM table read')
    args = parser.parse_args()
    timeDelta = args.time

    # Check we are root
    if os.geteuid() != 0:
        print("ERROR: This script must be run as root.\nRun as \"sudo ./getTQ.py\"")
        exit(1)

    # Check if EMANE is running
    try:
        EMANEEventChannel = EventService(('224.1.2.8', 45703, 'control0'))
    except OSError:
        print("ERROR: Can not find the event channel, is EMANE running?\n")
        exit(1)

    print(getOGMTable()[0])
