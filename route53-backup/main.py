#!/usr/bin/python3

import boto3
import json
import sys
from concurrent.futures import ThreadPoolExecutor, ALL_COMPLETED
from concurrent.futures import wait as ThreadWait
from botocore.config import Config
#sleepTest import time

boto_config = Config(region_name = 'us-east-1', retries = { 'max_attempts': 6, 'mode': 'standard' })

'''
Reference doc on backup and restore Route53 zones
  https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/hosted-zones-migrating.html
'''


def getResourceRecords(HostedZoneId, MaxItems=1):
  print("HostedZoneId: %s" % HostedZoneId)
  print("MaxItems: %s" % str(MaxItems))
  client = boto3.client('route53', config=boto_config)
  IsTruncated = True
  SRN = None
  SRT = None
  pool = ThreadPoolExecutor(5)
  filei = 0
  future = []
  while IsTruncated:
    if SRN and SRT:
      print("Requesting list_resource_record_sets pagination SRN:%s SRT:%s" % (SRN,SRT))
      r = client.list_resource_record_sets(HostedZoneId=HostedZoneId, MaxItems=str(MaxItems), StartRecordName=SRN, StartRecordType=SRT)
    else:
      print("Requesting list_resource_record_sets")
      r = client.list_resource_record_sets(HostedZoneId=HostedZoneId, MaxItems=str(MaxItems))
    rrs = r['ResourceRecordSets']
    future.append(pool.submit(formatResourceRecords, ResourceRecordSets=rrs, FileName=str(filei)))
    filei = filei+1
    IsTruncated = r['IsTruncated']
    if IsTruncated:
      SRN = r['NextRecordName']
      SRT = r['NextRecordType']
  not_done = 1
  while not_done > 0:
    print("Waiting for threads to finish")
    nd = ThreadWait(future, timeout=60, return_when=ALL_COMPLETED)
    not_done = len(nd.not_done)
  print("Threads are finished: %s" % str(not_done))
    

def formatResourceRecords(ResourceRecordSets, FileName):
  print("Formating resource records in a way we can import back easily. Filename: %s" % FileName)
  f = {'Action': 'UPSERT', 'ResourceRecordSet': ResourceRecordSets }
  with open(FileName+".json", 'w') as fn:
    fn.write(json.dumps(f))
  fn.close()
  #sleepTest time.sleep(5)


def main(args):
  print("Starting route53 backup for zone: %s" % args[0])
  getResourceRecords(HostedZoneId=args[0], MaxItems=100)


if __name__ == "__main__":
  main(sys.argv[1:])
