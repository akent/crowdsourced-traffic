#!/usr/bin/env python

import sys
import tweepy
import csv

accounts = {} # set of accounts to post to / from

accesskeyreader = csv.reader(open('access.key'), delimiter=',')
for row in accesskeyreader:
    CONSUMER_KEY = row[0]
    CONSUMER_SECRET = row[1]

accountreader = csv.reader(open('accounts.csv'), delimiter=',')

for row in accountreader:
    accounts[row[0]] = (row[1], row[2])

def main():
    for a in accounts.keys():
        print a
        postUpdate(a, "<status goes here>")

def getTweepyApi(acctname):
    ACCESS_KEY = accounts[acctname][0]
    ACCESS_SECRET = accounts[acctname][1]
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    return tweepy.API(auth)

def postUpdate(acctname, status):
    api = getTweepyApi(acctname)
    api.update_status(status)

if __name__ == "__main__":
    main()
