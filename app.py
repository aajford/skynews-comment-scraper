#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os import environ as env
from sys import argv

import bottle
from bottle import default_app, request, route, response, get

bottle.debug(True)

@get('/')
def index():
    response.content_type = 'text/plain; charset=utf-8'
    try:
        # For Python 3.0 and later
        from urllib.request import urlopen
        from urllib import HTTPError, URLError
    except ImportError:
        # Fall back to Python 2's urllib2
        from urllib2 import urlopen, HTTPError, URLError
    import json, base64, re
    from random import randint

    # Function to get json from a URL
    def get_jsonparsed_data(url):

        try:
           response = urlopen(url)
        except HTTPError, err:
           if err.code == 404:
               return "Page not found!"
           elif err.code == 403:
               return "Access denied!"
           else:
               return "Something happened! Error code", err.code
        except URLError, err:
            return "Some other error happened:", err.reason

        data = str(response.read())
        return json.loads(data);


    # URL for LivefyreAPI
    urlHottest = "https://bskyb.bootstrap.fyre.co/api/v3.0/hottest/?site=360818&number=5"

    done = 0
    maxTries = 5

    while done < maxTries:

        # Get the 'hottest' stories for comments
        jsonDataStories = get_jsonparsed_data(urlHottest)

        #Pick random story
        try:
            storiesNumber = len(jsonDataStories["data"])
            storiesNorm = randint(0,(storiesNumber - 1))

        except:
            done +=1
            continue

        try:

            # Read the 'Hottest' story title and ID
            articleTitle = jsonDataStories["data"][storiesNorm]["title"]
            articleID =  str(jsonDataStories["data"][storiesNorm]["articleId"])
            # Encode ID using Base 64
            articleIDBase64 = base64.b64encode(articleID)

        except:
            done +=1
            continue

        # Build URL for the top comments on the article 
        urlTopLikes = "http://bskyb.bootstrap.fyre.co/api/v3.0/site/360818/article/"+articleIDBase64+"/top/likes/"

        # Get top comments
        try: 
            jsonDataComments = get_jsonparsed_data(urlTopLikes)
            
        except: 
            done +=1
            continue

        # Pick a random comment

        try:
            ratedComments = len(jsonDataComments["data"]["content"])
            ratedCommentNorm = randint(0,(ratedComments - 1))
        except: 
            done +=1
            continue
        
        #Read Horrible Comment and number of likes
        try: 

            horribleCommentHTML = jsonDataComments["data"]["content"][ratedCommentNorm]["content"]["bodyHtml"]
            numberOfLikes = str(jsonDataComments["data"]["content"][ratedCommentNorm]["content"]["annotations"]["likes"])
        
        except: 
            done +=1
            continue

        #Strip out html tags
        def cleanhtml(raw_html):

            cleanr =re.compile('<.*?>')
            cleantext = re.sub(cleanr,'', raw_html)
            return cleantext;

        filth = cleanhtml(horribleCommentHTML)

        break

    if done == 5:
        
        return "{comment: \"Sorry, LiveFyre's API is being about as good as Vigiglobe's\"}"

    else:

        #print the horrible comment
        if numberOfLikes == "1" or numberOfLikes == "0":
            comment =  "{comment: \"" + filth + "\" - " + articleTitle + ", " + numberOfLikes + " like\"}"

        else:
            comment =  "{comment: \"" + filth + "\" - " + articleTitle + ", " + numberOfLikes + " likes\"}"


    return comment

bottle.run(host='0.0.0.0', port=argv[1])
