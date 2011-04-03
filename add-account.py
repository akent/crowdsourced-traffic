#!/usr/bin/python

import tweepy
import csv

accesskeyreader = csv.reader(open('access.key'), delimiter=',')
for row in accesskeyreader:
    CONSUMER_KEY = row[0]
    CONSUMER_SECRET = row[1]

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth_url = auth.get_authorization_url()
print 'Please authorize: ' + auth_url
verifier = raw_input('PIN: ').strip()
auth.get_access_token(verifier)

print "ACCESS_KEY = '%s'" % auth.access_token.key
print "ACCESS_SECRET = '%s'" % auth.access_token.secret

accountwriter = csv.writer(open('accounts.csv', 'a'), delimiter=',')
accountwriter.writerow([auth.get_username(), auth.access_token.key,
        auth.access_token.secret])
