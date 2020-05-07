# What_to_track_on_Twitter_Streaming_API
Code for Sumeet Kumar, Kathleen M. Carley, What to Track on the Twitter Streaming API? A Knapsack Bandits Approach to Dynamically Update the Search Terms,  ASONAM Conference, Vancouver, Canada, 2019 [link](https://ieeexplore.ieee.org/document/9073274)

# Before running the code
Put your Twitter tokens at the following location - '../twitter_tokens.json' in format: {"consumer_key":"", "consumer_secret" : "", "access_token" : "", "access_token_secret" : ""}
Create './result/' directory


# Code to run to collect data

```
import json
from Twitter_Topic_Tracker.streaming_service import *
from Twitter_Topic_Tracker.knapsack import *
from Twitter_Topic_Tracker.text_classifier import *
from Twitter_Topic_Tracker.text_processor import *

tweetsPath = "./result/" #data
acl_tweetsPath = "./data/ACL_ICWSM_2018_datasets/nepal/"


# how many past interation data to use to get new serach terms e.g., 10
ucb_cost_value_estimator = Cost_Value_Estimator(10) 
mean_cost_value_estimator = Cost_Value_Estimator(1) # does not use data from previous iterations
mean_10_cost_value_estimator = Cost_Value_Estimator(10)
TARGET_TIME = 2 # minutes     

def read_twitter_tokens(twitter_token_path = '../twitter_tokens.json'):
    json_data = {}

    with open(twitter_token_path, 'r') as json_read:
        for line in json_read:
            json_data = json.loads(line)

    return json_data['consumer_key'], json_data['consumer_secret'], json_data['access_token'], json_data['access_token_secret']


consumer_key, consumer_secret, access_token, access_token_secret = read_twitter_tokens()
collection_count = 40

text_clf_svm = get_trained_classifier(acl_tweetsPath)

try:
    while(True):
        start_time = datetime.now()
        new_tweets, rate_error = collect_data(tweetsPath, consumer_key, consumer_secret, access_token, access_token_secret, collection_count, terms= search_terms)
        
        end_time = datetime.now()

        time_taken = ((end_time - start_time).seconds/ 60.0) # per minute
        print('collection_count', collection_count, 'time_taken minutes: ', str(time_taken))

        if int(time_taken) < TARGET_TIME:
            collection_count = int(2* collection_count)
            print('taking less time, increasing the colection count', collection_count)
        else:
            if int(time_taken) > TARGET_TIME + 3:
                print('taking more time, check to decrease the collection rate')
                #if collection_count > 200:
                collection_count = int(0.9*collection_count)

        print('new collection_count', collection_count)

        new_tweets_formated = get_cleaned_collected_data(new_tweets)    
        tag_tweets, __ = get_tags_with_tweets(new_tweets_formated)    

        search_terms = get_new_search_terms(text_clf_svm, tag_tweets, time_taken, ucb_cost_value_estimator, mean_cost_value_estimator, mean_10_cost_value_estimator)
        print('next search terms: ', search_terms)

except KeyboardInterrupt:
    print('interrupted!')
    sys.exit()

except Exception as ex:
    print(ex)
    
```


# Code to plot the results
After you have run tht code for a few days, please check the Ipython Notebook to visulaize the results.

## If you use this code, please cite the following paper:
Sumeet Kumar, Kathleen M. Carley, What to Track on the Twitter Streaming API? A Knapsack Bandits Approach to Dynamically Update the Search Terms,  ASONAM Conference, Vancouver, Canada, 2019 link
