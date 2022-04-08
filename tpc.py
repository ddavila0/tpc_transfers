#!/usr/bin/env python3

# This script is used to cook curl commands that will perform actions similar to those in a Third Part Copy transfer
# done through FTS: request macaroon, download file, upload file, copy, get checksum, etc.

# TODO:
# * validatex509 credentials
# * Check that extract_macaroon works when curl_debug =1
# - automatic suffix 
# - trigger parallel transfers
# - verify with checksum
# - add an arg parser
#   -- pass x509 cert and key as arguments
#   -- pass source and dest enpoint as arguments


import sys
import argparse
import logging
import time
import subprocess
import pdb
import os
import configparser
import datetime
from multiprocessing import Process, Value, Lock
from tpc_utils import *

#pdb.set_trace()
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v", help="Verbose", action="store_true")
    parser.add_argument("--use_x509", help="Use only x509 and not macaroons", action="store_true")
    parser.add_argument("source", help="Source URL")
    parser.add_argument("destination", help="Destination URL")
    return parser.parse_args()


def main():
    #---- Read arguments-------------------------------------------------------- 
    args = parse_args()
    use_x509= args.use_x509
    url_src = args.source
    url_dst = args.destination
    if not "https" in url_src or not "https" in url_dst:
        print("ERROR: URLs have to start with https")
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
    
    log.info("Making TPC: "+url_src+" -> "+url_dst)
    macaroon_src = macaroon_dst = None
    if not use_x509:
    # Get macaroons
        log.info("Requesting macaroons")
        macaroon_src = tpc_util.request_macaroon(url_src, "DOWNLOAD,DELETE,LIST")
        macaroon_dst = tpc_util.request_macaroon(url_dst, "UPLOAD,DELETE,LIST")
        if(not macaroon_src):
            log.info("Could not get src macaroon")
            exit(1)
        if(not macaroon_dst):
            log.info("Could not get dst macaroon")
            exit(1)
    # Start TPC
    log.info("Starting transfer")
    res = tpc_util.tpc(url_src, macaroon_src, url_dst, macaroon_dst, verbose=True)

    ## Get Checksum 
    #if(res == 0):
    #    log.info("Getting checksums")
    #    adler32_src = tpc_util.get_adler32(url_src, macaroon_src)
    #    adler32_dst = tpc_util.get_adler32(url_dst, macaroon_dst)

    #    if((adler32_src is None) or (adler32_dst is None)):
    #        log.error("Could not get one of the adler32s")

    #    elif(adler32_src == adler32_dst):
    #        log.info("adler32 matches")
    #    else: 
    #        log.error("adler32 doesn't match")
    #        log.error("adler32_src: "+adler32_src)
    #        log.error("adler32_dst: "+adler32_dst)

log = logging.getLogger()    
if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
