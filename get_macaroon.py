#!/usr/bin/env python
import sys
import os
import logging
import ConfigParser
import argparse
#from pymacaroons import Macaroon, Verifier
from tpc_utils import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", help="Verbose", action="store_true")
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
        configParser = ConfigParser.RawConfigParser()
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
    #macaroon = tpc_util.request_macaroon(url, "DOWNLOAD,LIST")
    macaroon = tpc_util.request_macaroon(url, "DOWNLOAD,LIST,READ_METADATA")
    if macaroon:
        log.info("Macaroon:\n"+macaroon)
        try:
            n = Macaroon.deserialize(macaroon)
            log.debug("Macaroon deserialized:\n"+n.inspect())
        except:
            log.debug("Cannot deserialize the macaroon")
    else:
        log.error("Cannot get the macaroon")


log = logging.getLogger()    
if __name__ == "__main__":
    main()
