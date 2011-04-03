#!/usr/bin/python

# Project: twitter-repeater
# Author: Charles Hooper <chooper@plumata.com>
#
# Copyright (c) 2010, Charles Hooper
# All rights reserved.
#
# Modified for sydneytraffic by Adam Kent <adam@semicircular.net>
#
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# * Neither the name of Plumata LLC nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific prior
# written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.

import sys
import os
import string
import re
import tweepy
import oauthpost

# import exceptions
from urllib2 import HTTPError

# globals - The following is populated later by load_lists
IGNORE_LIST = []
FILTER_WORDS = []

tweet_as_user = "sydtraffic_cs"
ignore_list='ignore.txt'   # List of twitter screen names to ignore
filtered_word_list='filter.txt'    # Ignore tweets if they contain these words
last_id_file='lastid.txt'  # Last ID the bot "saw"

def debug_print(text):
    """Print text if debugging mode is on"""
    print text

def save_id(statefile,id):
    """Save last status ID to a file"""
    last_id = get_last_id(statefile)

    if last_id < id:
        debug_print('Saving new ID %d to %s' % (id,statefile))
        f = open(statefile,'w')
        f.write(str(id)) # no trailing newline
        f.close()
    else:
        debug_print('Received smaller ID, not saving. Old: %d, New: %s' % (
            last_id, id))


def get_last_id(statefile):
    """Retrieve last status ID from a file"""

    try:
        f = open(statefile,'r')
        id = int(f.read())
        f.close()
    except IOError:
        debug_print('IOError raised, returning zero (0)')
        return 0
    return id


def load_lists(force=False):
    """Load ignore and filtered word lists"""
    debug_print('Loading ignore list')
    if not IGNORE_LIST or force is True:
        global IGNORE_LIST
        IGNORE_LIST = [
            line.lower().strip() for line in open(ignore_list) ]

    debug_print('Loading filtered word list')
    if not FILTER_WORDS or force is True:
        global FILTER_WORDS
        FILTER_WORDS = [
            line.lower().strip() for line in open(filtered_word_list) ]


def careful_retweet(api,reply):
    """Perform retweets while avoiding loops and spam"""

    load_lists()

    debug_print('Preparing to retweet #%d' % (reply.id,))
    normalized_tweet = reply.text.lower().strip()

    # Don't try to retweet our own tweets
    if reply.from_user.lower() == tweet_as_user:
        return

    # Don't retweet if the tweet is from an ignored user
    if reply.from_user.lower() in IGNORE_LIST:
        return

    # Don't retweet if the tweet contains a filtered word
    for word in normalized_tweet.split():
        if word.lower().strip() in FILTER_WORDS:
            return

    # Don't retweet directed @ replies
    if reply.text[0] == '@' and (reply.text.find("@sydneytraffic") == -1) and (reply.text.find("@sydtraffic_") == -1):
        return

    # HACK: Don't retweet if tweet contains more usernames than words (roughly)
    username_count = normalized_tweet.count('@')
    if username_count >= len(normalized_tweet.split()) - username_count:
        return

    # Try to break retweet loops by counting the occurences tweeting user's name
    if normalized_tweet.split().count('@'+ reply.from_user.lower()) > 0:
        return

    debug_print('Retweeting #%d' % (reply.id,))
    return api.retweet(id=reply.id)

def try_it(result):
    api = oauthpost.getTweepyApi(tweet_as_user)

    last_id = get_last_id(last_id_file)
    if result.id > last_id:
        print "Got new tweet with id: %d" % result.id
        try:
            careful_retweet(api, result)
        except HTTPError, e:
            print e.code()
            print e.read()
        except Exception, e:
            print 'e: %s' % e
            print repr(e)
        else:
            save_id(last_id_file, result.id)

def main():
    api = oauthpost.getTweepyApi(tweet_as_user)

    last_id = get_last_id(last_id_file)

    try:
        results = api.search("#sydneytraffic")
    except Exception, e:    # quit on error here
        print e
        sys.exit(1)

    for result in results:
        # ignore tweet if it's id is lower than our last tweeted id
        if result.id > last_id:
            try:
                careful_retweet(api, result)
            except HTTPError, e:
                print e.code()
                print e.read()
            except Exception, e:
                print 'e: %s' % e
                print repr(e)
            else:
                save_id(last_id_file, result.id)

def retweet_by_id(i):
    api = oauthpost.getTweepyApi(tweet_as_user)
    print i
    return api.retweet(id=i)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        print sys.argv
        retweet_by_id(sys.argv[1])
        sys.exit(0)
    try:
        main()
    except KeyboardInterrupt:
        quit()

