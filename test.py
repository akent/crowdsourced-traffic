#!/usr/bin/python

import classifier
import oauthpost
import sys
import codecs
import retweeter
import time

IGNORE_LIST = []
FILTER_WORDS = []

ignore_list='ignore.txt'   # List of twitter screen names to ignore
filtered_word_list='filter.txt'    # Ignore tweets if they contain these words

if not IGNORE_LIST or force is True:
    IGNORE_LIST = [
        line.lower().strip() for line in open(ignore_list) ]

if not FILTER_WORDS or force is True:
    FILTER_WORDS = [
        line.lower().strip() for line in open(filtered_word_list) ]

SYDNEY_GEOCODE = "-33.859972,151.21111,100km"
searches = [
            ("sydneytraffic, ""),
           ]

useful = []
useless = []
unsure = []

def post_search_filter(result):
    normalized_tweet = result.text.lower().strip()

    # Don't retweet if the tweet is from an ignored user
    if result.from_user.lower() in IGNORE_LIST:
        return False

    # Don't retweet if the tweet contains a filtered word
    for word in normalized_tweet.split():
        if word.lower().strip() in FILTER_WORDS:
            return False

    # Don't retweet directed @ replies
    if result.text[0] == '@' and (result.text.find("@sydneytraffic") == -1) and (result.text.find("@sydtraffic_") == -1):
        return False

    # remove 4sq.com
    if result.text.find("4sq.com") != -1:
        return False

    return True


def do_one_search(search, gc):
    print search

    try:
        results = api.search(search, geocode=gc, rpp=10)
    except Exception, e:    # quit on error here
        print e
        sys.exit(1)

    for result in results:
        if (not post_search_filter(result)):
            print "discarding: %s %s" % (result.from_user, result.text)
            continue
        text = "%s %s" % (result.from_user, result.text.strip())
        category = classifier.process(text)
        if category == "traffic":
            useful.append(result)
        elif category == "unsure":
            unsure.append(result)
        elif category == "useless":
            useless.append(result)

api = oauthpost.getTweepyApi("sydtraffic_cs")

for search in searches:
    do_one_search(search[0], search[1])

useful.sort(key=lambda result: result.id)
unsure.sort(key=lambda result: result.id)
useless.sort(key=lambda result: result.id)


print "Traffic:"
for result in useful:
    print "%s %s %s" % (result.id, result.from_user, result.text)

print "\n\nUnsure:"
for result in unsure:
    print "%s %s %s" % (result.id, result.from_user, result.text)

print "\n\nUseless:"
for result in useless:
    print "%s %s %s" % (result.id, result.from_user, result.text)

print "\n\n"
time.sleep(10)

for result in useful:
    retweeter.try_it(result)
    pass

print "Complete\n"
