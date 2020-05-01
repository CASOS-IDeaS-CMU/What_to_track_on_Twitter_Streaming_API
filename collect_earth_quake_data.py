
# Read data and load last 2000 tweets for each hashtag
# Load labeled pro and con data
# Build calssifiers based on data associated with hashtags
# Get the perfromance of the classifiers based on the validation set
# Pick top m hashtags good for classification
import json
from Twitter_Topic_Tracker.streaming_service import *
from Twitter_Topic_Tracker.knapsack import *
from Twitter_Topic_Tracker.text_classifier import *
from Twitter_Topic_Tracker.text_processor import *

tweetsPath = "./result/" #data
acl_tweetsPath = "./data/ACL_ICWSM_2018_datasets/nepal/"


ucb_cost_value_estimator = Cost_Value_Estimator(10)
mean_cost_value_estimator = Cost_Value_Estimator(1) # does not use data from previous iterations
mean_10_cost_value_estimator = Cost_Value_Estimator(10)
TARGET_TIME = 2 # minutes     


# while(True):
# new_tweets_samples_for_simulation = []
# for m in range(1, 10):
#while(True):

def read_twitter_tokens(twitter_token_path = '../twitter_tokens.json'):
    json_data = {}

    with open(twitter_token_path, 'r') as json_read:
        for line in json_read:
            json_data = json.loads(line)

    return json_data['consumer_key'], json_data['consumer_secret'], json_data['access_token'], json_data['access_token_secret']


consumer_key, consumer_secret, access_token, access_token_secret = read_twitter_tokens()
collection_count = 400

text_clf_svm = get_trained_classifier(acl_tweetsPath)

try:
    while(True):
        #collection_count = 400
        start_time = datetime.now()
        new_tweets, rate_error = collect_data(tweetsPath, consumer_key, consumer_secret, access_token, access_token_secret, collection_count, terms= search_terms)

#        if rate_error:
#            
#            collection_count = 2* collection_count
#            print('got rate error, new colection count', collection_count)
#        else:
#            print('no rate error, check to decrease the collection rate')
#            if collection_count > 200:
#                collection_count = 0.9*collection_count
        
        end_time = datetime.now()

        time_taken = ((end_time - start_time).seconds/ 60.0) # per minute
        print('collection_count', collection_count, 'time_taken minutes: ', str(time_taken))

    #         new_tweets_samples_for_simulation.append(new_tweets)

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

       # break

