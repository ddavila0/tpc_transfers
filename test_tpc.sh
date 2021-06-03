#!/bin/bash

ENDPOINT=$1
RSE=$2
FILE=$3
USERNAME=$(voms-proxy-info --subject | awk -F "/" '{print $6}' | awk -F "=" '{print $2}')
FTS_SERVER="https://fts3-cms.cern.ch:8446" 
#FTS_SERVER="https://cmsfts3.fnal.gov:8446" 

TPC_DEST1="davs://redirector.t2.ucsd.edu:1094/store/user/$USERNAME/TPC/$RSE/$FILE"
#TPC_DEST1="davs://xrootd-local.unl.edu:1094/store/temp/user/$USERNAME/TPC/$RSE/$FILE"
TPC_SOURCE2=$TPC_DEST1

echo "Testing: "$ENDPOINT

# Test I can write to endpoint
echo "Checking I can write to $ENDPOINT/store/temp/user/$USERNAME/$FILE"
gfal-copy -f -p $(pwd)/$FILE $ENDPOINT/store/temp/user/$USERNAME/$FILE

if [ $? -eq 0 ]; then
    echo gfal-copy: OK
else
    echo: gfal-copy: FAILED
    exit
fi


# Test FTS TPC Endpoint as Source
TPC_SOURCE="$ENDPOINT/store/temp/user/$USERNAME/$FILE"

TRANSFER_ID=$(fts-transfer-submit -o --compare-checksums -s $FTS_SERVER $TPC_SOURCE $TPC_DEST1) 
echo "TRANSFER ID: "$TRANSFER_ID

RESULT=$(fts-transfer-status -s $FTS_SERVER $TRANSFER_ID)
while [ $RESULT != "FINISHED" ] && [ $RESULT != "FAILED" ]
do
  echo "RESULT: $RESULT"
  sleep 5
  RESULT=$(fts-transfer-status -s $FTS_SERVER $TRANSFER_ID)
done

if [ $RESULT == "FINISHED" ]
then
  echo fts-transfer-submit endpoint as source: OK
else [ $RESULT == "FAILED" ]
  echo fts-transfer-submit endpoint as source: FAILED
  exit
fi


# Test FTS TPC Endpoint as Destination
TPC_DEST="$ENDPOINT/store/temp/user/$USERNAME/TPC_WRITE/$FILE"

TRANSFER_ID=$(fts-transfer-submit -o --compare-checksums -s $FTS_SERVER $TPC_SOURCE2 $TPC_DEST)
echo "TRANSFER ID: "$TRANSFER_ID

RESULT=$(fts-transfer-status -s $FTS_SERVER $TRANSFER_ID)
while [ $RESULT != "FINISHED" ] && [ $RESULT != "FAILED" ]
do
  echo "RESULT: $RESULT"
  sleep 5
  RESULT=$(fts-transfer-status -s $FTS_SERVER $TRANSFER_ID)
done

if [ $RESULT == "FINISHED" ]
then
  echo fts-transfer-submit endpoint as destination: OK
else [ $RESULT == "FAILED" ]
  echo fts-transfer-submit endpoint as destination: FAILED
  exit
fi
 
