#!/usr/bin/env python3
import sys
import os
import logging
import configparser
import argparse
from pymacaroons import Macaroon, Verifier
from tpc_utils import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", help="Verbose", action="store_true")
    parser.add_argument("--ipv4", "-4", help="ipv4", action="store_true")
    parser.add_argument("--ipv6", "-6", help="ipv6", action="store_true")
    parser.add_argument("source", help="Source URL")
    return parser.parse_args()


def main():
    #---- Read arguments-------------------------------------------------------- 
    args = parse_args()
    url = args.source
    if not "https" in url:
        print("ERROR: URL has to start with https")
        sys.exit(1)
    #---------------------------------------------------------------------------

    #----- Config --------------------------------------------------------------
    # Set the logging level
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s  %(levelname)s - %(message)s', datefmt='%Y%m%d %H:%M:%S')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s  %(levelname)s - %(message)s', datefmt='%Y%m%d %H:%M:%S')
    
    # Check that the configuration file exists
    if os.path.isfile(".config"):
        configParser = configparser.RawConfigParser()
        configParser.read(".config")
        
        curl_debug = configParser.getint('all', 'curl_debug')
        proxy      = configParser.get('all', 'proxy')
        timeout    = configParser.getint('all', 'timeout')
    else:
        # If the .config file doesn't exist, set the defaults        
        curl_debug = 1
        proxy= "/tmp/x509up_u0"
        timeout = 120

    #---------------------------------------------------------------------------
    
  
    tpc_util = TPC_util(log, timeout, curl_debug, proxy)
    caveats="UPLOAD,DOWNLOAD,LIST,READ_METADATA"
    #caveats="DOWNLOAD,LIST"
    if args.ipv4:
        macaroon = tpc_util.request_macaroon(url, caveats, "-4")
    elif args.ipv6:
        macaroon = tpc_util.request_macaroon(url, caveats, "-6")
    else:
        macaroon = tpc_util.request_macaroon(url, caveats)
    if macaroon:
        log.info("Macaroon:\n"+macaroon)
        try:
            n = Macaroon.deserialize(macaroon)
            log.info("Macaroon deserialized:\n"+n.inspect())
        except:
            log.info("Cannot deserialize the macaroon")
    else:
        log.error("Cannot get the macaroon")


log = logging.getLogger()    
if __name__ == "__main__":
    main()
