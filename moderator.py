#!/usr/bin/python

import tweepy
import string
import shelve
from oauthpost import getTweepyApi

from hashlib import sha1

post_account = "sydtraffic_cs"
moderator_account = "akent"
api = getTweepyApi(post_account)
history = shelve.open(".histfile-moderator")

def msg_hash(text):
	return sha1(text).hexdigest()[:7]

def ask(text):
	hash_str = msg_hash(text)
	to_send = "%s %s" % (hash_str, text)[:140]
	sent = api.send_direct_message(screen_name = moderator_account, text = to_send)
	history[hash_str] = text

def take_action(action, text):
	print "Got %s on text: %s" % (action, text)

def parse_response(text, user):
	spl = text.split(" ", 2)
	if (len(spl) < 2): return
	hash = spl[0]
	action = spl[1]
	if history.has_key(hash) and user == moderator_account:
		take_action(action, history[hash])

def check_for_responses():
	for message in api.direct_messages(count=6):
		parse_response(message.text, message.sender_screen_name)

def main():
	#id = ask("So many parts of Anzac Pde under water #sydneytraffic")
	#ask("@sydneytraffic pitterwater rd is the only road, what's why all the time congestion. www.onlineabc.com.au")
	check_for_responses()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        quit()


history.close()
