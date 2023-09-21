#!/usr/bin/env python3

import argparse
import os
from emane.events import EventService, LocationEvent, PathlossEvent
import subprocess
import sys
import psutil

# Argument checker for time argument
class TimeAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if(values < 1):
            parser.print_usage(sys.stderr)
            print("error: OGM Table only refreshes every second, timeDelta must be 1 second or greater")
            sys.exit(-1)
        setattr(namespace, self.dest, values)


def getOGMTable():
    ogmTable = "batctl o"
    proc_out = subprocess.run(args=ogmTable,
                              shell=True,
                              universal_newlines=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL)
    table_list = proc_out.stdout.split("\n")
    
    # currNEM = table_list[0][]


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
    # Args List:
    #   -t, --time: Measure of how often the OGM table is recorded

    toolDesc = "A tool to retrieve the transmission quality metric from the B.A.T.M.A.N. routing algorithm.\nThis tool must be run as root.\nEMANE must be running.\n"

    parser = argparse.ArgumentParser(description=toolDesc,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--time', '-t',
                        action=TimeAction,
                        type=int,
                        nargs='?',
                        default=1,
                        help='Number of seconds between OGM table read')
    args = parser.parse_args()
    timeDelta = args.time

    # Check we are root
    if(os.geteuid() != 0):
        parser.print_usage(sys.stderr)
        print("error: This script must be run as root. Run as \"sudo ./getTQ.py\"")
        sys.exit(-1)

    # Check if EMANE is running
    try:
        EMANEEventChannel = EventService(('224.1.2.8', 45703, 'control0'))
    except OSError:
        print("error: Can not find the event channel, is EMANE running?\n")
        sys.exit(-1)

    # Check we are inside an EMANE NEM
    # (Look to see if the "bat0" interface exists)
    if("bat0" not in psutil.net_if_addrs()):
        parser.print_usage(sys.stderr)
        print("error: This script must be run inside an EMANE NEM")
        sys.exit(-1)

    print(getOGMTable()[0])
    print(getOGMTable()[1])