#!/usr/bin/python
import json
import os.path

# Configuration
# infoo.json should contain:
#   GOOGLE_ID
#   GOOGLE_SECRET
#   SECRET_KEY

if not os.path.isfile('info.json'):
    print "Please provide the following information. This will be saved in info.json", \
          "and used for future requests\n"

    infoIn = {
        'consumer_key'    : raw_input("Google Consumer Key: "),
        'consumer_secret' : raw_input("Google Consumer Key: "),
        'secret_key'      : raw_input("App Secret Key: ")
    }

    with open('info.json', 'w') as outfile:
        json.dump(infoIn, outfile)

with open('info.json', 'r') as infile:
    global info
    info = json.load(infile)
