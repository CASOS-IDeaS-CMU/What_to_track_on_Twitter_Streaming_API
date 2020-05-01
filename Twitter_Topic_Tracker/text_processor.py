import os, urllib
import json
import sys
import operator
import unicodedata
import string
import re
import random
from os import listdir
from os.path import isfile, join



all_letters = string.ascii_letters + " .,;'"
n_letters = len(all_letters)

# Turn a Unicode string to plain ASCII, thanks to http://stackoverflow.com/a/518232/2809427
def unicodeToAscii(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
        and c in all_letters
    )


def clean_text(string):
    #remove @mentions
    # remove URLS
    string = re.sub(r"(?:\@|https?\://)\S+", "", string)
#     string = string.replace('#' , '').lower()
#     return re.sub("[^a-zA-Z]", "", string) # or should we just get unicode
    string = string.replace('RT', '')
    return unicodeToAscii(string)

def get_hashtagsall_and_at_the_end_of_sentence(label, tweet):
    text = ""
    
    if 'full_text' in tweet:
        text = tweet['full_text']
    else:
        text = tweet['text']
                    
    if 'extended_tweet' in tweet:
        extended_tweet = tweet['extended_tweet']

        if 'full_text' in extended_tweet:
            text = extended_tweet['full_text']

    
    words = text.strip().replace('\n', ' ').replace(',', ' ').split(' ')
    end_tags = []
    
    tags = []
    tags_index = []
    endtag_free_text = ""
    
    last_plain_word_index = 0
    if len(words) > 0:
        midlle_tags = 0
        for i, word in enumerate(words):
            if '#' in word and '.' not in word:
                tag_val = '#' + word.split('#')[1]
                tags.append(tag_val.lower()) #clean_text(
                tags_index.append(i)
                midlle_tags += 1
            else:
                last_plain_word_index = last_plain_word_index +midlle_tags + 1
                midlle_tags = 0

        for index, tag in zip(tags_index, tags):
            if index >= last_plain_word_index and len(tag)> 1 :
                end_tags.append(tag)

        

        for i, word in enumerate(words):
            if i < last_plain_word_index:
                endtag_free_text = endtag_free_text  + ' ' +  word
            
    return tags, end_tags, clean_text(endtag_free_text) #clean_text(

def get_tags_with_tweets(tweets):
    tag_tweets = {}
    co_hashtags = {}
    
    for tweet in tweets:
        try:
            text_org_for_quote = None
            if 'retweeted_status' in tweet:

                retweeted_status = tweet['retweeted_status']
                hashtags, endtags, text = get_hashtagsall_and_at_the_end_of_sentence('RTweetOrig',tweet)

            elif 'quoted_status' in tweet:    
                quoted_status = tweet['quoted_status']

                hashtags, endtags, text = get_hashtagsall_and_at_the_end_of_sentence('QTweet', quoted_status)
                hashtags, endtags, text_org_for_quote = get_hashtagsall_and_at_the_end_of_sentence('QTweetOriginal',tweet)

            elif 'in_reply_to_status_id' in tweet:

                hashtags, endtags, text = get_hashtagsall_and_at_the_end_of_sentence('ReplyTweet', tweet)
            else:

                hashtags, endtags, text = get_hashtagsall_and_at_the_end_of_sentence('Tweet', tweet)

            for tag in hashtags:
                if tag not in tag_tweets:
                    tag_tweets[tag] = {}

                if text not in tag_tweets[tag]:
                    tag_tweets[tag][text] = 1
                else:
                    tag_tweets[tag][text] = tag_tweets[tag][text]  + 1

                if text_org_for_quote is not None:
                    if text_org_for_quote not in tag_tweets[tag]:
                        tag_tweets[tag][text_org_for_quote]  = 1
                    else:
                        tag_tweets[tag][text_org_for_quote]  = tag_tweets[tag][text_org_for_quote]   + 1

            if len(hashtags) > 1:    
                for i, tag1 in enumerate(hashtags):
                    for j, tag2 in enumerate(hashtags):
                        if i != j:
                            if tag1 not in co_hashtags:
                                co_hashtags[tag1] = [tag2]
                            else:
                                co_hashtags[tag1].append(tag2)
        except Exception as ex:
            print(" could not load tweet" + json.dumps(tweet))
            print(sys.exc_info()) 
                            
    return tag_tweets, co_hashtags


