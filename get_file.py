#!/usr/bin/env python
import sys
import os
import logging
import ConfigParser
import argparse
from tpc_utils import *
import pdb

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", help="Verbose", action="store_true")
    parser.add_argument("--use_x509", help="Use only x509 and not macaroons", action="store_true")
    parser.add_argument("source", help="Source URL")
    parser.add_argument("dest", help="Destination path")
    return parser.parse_args()


def main():
    #---- Read arguments-------------------------------------------------------- 
    args = parse_args()
    url             = args.source
    use_x509        = args.use_x509
    new_filename    = args.dest

    if not "https" in url:
        print("URL has to start with https")
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
    
    macaroon = None
    if not use_x509:
        macaroon = tpc_util.request_macaroon(url, "DOWNLOAD,LIST")
    tpc_util.get_file(url, macaroon, new_filename)

log = logging.getLogger()    
if __name__ == "__main__":
    main()
