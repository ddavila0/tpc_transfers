#!/usr/bin/env python
import sys
import os
import logging
import ConfigParser
import argparse
from tpc_utils import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", help="Verbose", action="store_true")
    parser.add_argument("--use_x509", help="Use only x509 and not macaroons", action="store_true")
    parser.add_argument("--token", help="Use provided token")
    parser.add_argument("filepath", help="file to be sent")
    parser.add_argument("dest", help="Destination URL")
    return parser.parse_args()


def main():
    #---- Read arguments-------------------------------------------------------- 
    args = parse_args()
    url             = args.dest
    use_x509        = args.use_x509
    filepath        = args.filepath

    if not "https" in url:
        print("Error:URL has to start with https")
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
	if args.token:
		macaroon = args.token
	else:
        	macaroon = tpc_util.request_macaroon(url, "UPLOAD,LIST")
    tpc_util.put_file(url, macaroon, filepath, verbose=args.verbose)

log = logging.getLogger()    
if __name__ == "__main__":
    main()
