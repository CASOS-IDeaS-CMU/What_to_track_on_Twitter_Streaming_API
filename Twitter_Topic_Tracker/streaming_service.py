from datetime import datetime
import tweepy
import requests
import json
import sys
import codecs
import time
import traceback
from datetime import datetime




def collect_data(tweetsPath, consumer_key, consumer_secret, access_token, access_token_secret, tweets_count_to_collect, terms=['#earthquake', '#tsunami', 'earthquake', 'tsunami']):

    new_tweets = []
    rate_error = False

    # consumer_key = "JflKYuYqaJvGNkPaZnImasKyS"
    # consumer_secret = "4NnZJjqyuQHolgoJRrBHdmEjE68ZI2Hl5aJmFFtQEh7IsYaaH9"
    # access_token = "159404488-0kY7styL2iWoF8f7FWk1Sk2Q2yAluNzOQrZCL4ID"
    # access_token_secret = "hz1CmckrUmEnB1Jx0rBhJun6P8F5C23mJpiCi3uYj5PCh"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    storePath = tweetsPath + "/"
    # terms = ['cyberattack', 'cybersecurity', 'cyberwar', 'DDOS', 'cyberhack', 'cyberespionage', 'cyberrisk']
    # terms = ['@INCIndiaLive', '@narendramodi', '#RafaleDeal', '#RahulGandhi', '#NamoAgain', '#NaMoAgain', '#RafaleScam', '#MeraParivarBhajapaParivar', '#Modi4NewIndia', '#PriyankaGandhi', '#PhirEkBaarModiSarkar', '#2019Election', '#MeraParivarBhajpaParivar', 'indian election', 'election in india', 'india election', '@RahulGandhi','@INCIndia']
    GEOBOX_WORLD = [-180,-90,180,90]
    
    
#     data_count = 0
#     tweets_count_to_collect = 10

    class StdOutListener(tweepy.StreamListener):

        def __init__(self, api=None):
            super(StdOutListener, self).__init__()
            self.num_tweets = 0
            self.start = datetime.utcnow()
            self.write = codecs.open(storePath+'tweets_'+str(self.start.month)+'_'+str(self.start.day)+".json",'a','utf-8')
            time_now = datetime.now()
            self.write.write('time:{}\n'.format(str(time_now)))


        def on_data(self, data):
#             global write
#             global start

#             data_count += 1
            try:
#                 print('data_count: ', data_count)
                self.write.write(str(data))
            except Exception as e:
                print(e)
                print(str(data))

            end = datetime.utcnow()
#             global start
            if(end.day != self.start.day):
                self.start = end
                write.close()
                write = codecs.open(storePath+'tweets_'+str(self.start.month)+'_'+str(self.start.day)+".json",'a','utf-8')

            self.num_tweets += 1
            if self.num_tweets < tweets_count_to_collect:
#                 print(self.num_tweets)
    #             collection.insert(record)
                new_tweets.append(str(data))
                return True
            else:
                return False

        def on_limit(self,status):
            print ("Rate Limit Exceeded, Sleep for 1 Mins")
            time.sleep(60)
            self.num_tweets = self.num_tweets * 2 # get more data in a batch
            rate_error = True
            return True

        def on_error(self, status):
            if(status== 420):
                rate_error = True
                self.num_tweets = self.num_tweets * 2
                print('Because of error, updating the number of tweets to download: ', self.num_tweets)
            print('error status', status)

    #     if __name__ == '__main__':
    l = StdOutListener()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = tweepy.Stream(auth, l)
#     while(True):
    try:
        stream.filter(track=terms ,encoding='utf-8') #locations=GEOBOX_WORLD,
    except KeyboardInterrupt:
        print('keyboard interruptions detected')
        stream.disconnect()
#         break
    except Exception as e:
        print (time.gmtime())
        print ("severe problem", e)
#         continue
    print('rate_error: ', rate_error)

    return new_tweets, rate_error


def get_cleaned_collected_data(new_tweets):
    new_tweets_formated = []
    for tweet in new_tweets:
        formated_tweet = json.loads(tweet)
        if 'lang' in tweet:
            language = formated_tweet['lang']
        else:
            language = None

        if 'id_str' not in formated_tweet or language != 'en': # for now the classifier only works for english language
            continue
        else:
            new_tweets_formated.append(formated_tweet)
            
    return new_tweets_formated

earthquake_terms = ['#earthquake', 'earthquake']
search_terms = earthquake_terms.copy()


def get_tag_values_and_count(text_clf_svm, tag_tweets, time_taken):
    
    tag_values_update= {}
    for tag, tweets in tag_tweets.items():
        tweets_text = list(tweets.keys())
        tweets_count = list(tweets.values())

        predicted = np.array(text_clf_svm.predict(tweets_text))
        tag_count_per_minute = np.divide(np.array(tweets_count), 1.0*time_taken)

        if np.mean(predicted) > 0.01: # otherwise getting a lot of junk
            value_count = [] #'t5':  [(0.2, 1), (0.1,2)]
            for count, value in zip(tag_count_per_minute, predicted):
                value_count.append((value, count))

            tag_values_update[tag] = value_count


    return tag_values_update


KNAPSACK_LIMIT = 2800
def knapsack_solver(cost_value, knapsack_terms):
    next_search_terms = []
    if len(cost_value)> 0:
        
        total_value = 0.0
        
        for (cost, value, index) in cost_value:
            total_value +=  value
        
        if total_value > KNAPSACK_LIMIT:
            total_cost, total_value, picked_indexes = knapsack(cost_value, KNAPSACK_LIMIT ) # max get 2900 tweets per minute
        else:
            picked_indexes = range(0, len(cost_value))

        for index in picked_indexes:
            next_search_terms.append(knapsack_terms[index].replace('(', '').replace(')', '')) # some cleaning is necessary
            
    return next_search_terms
 
stop_terms = ['fuck', 'pussy', 'ass',  'slut', 'blowjob', 'porn', 'nude' , 'sex', 'bbmas', 'exo', 'bbmastopsocial', 'cum', 'babe' , 'lesbian', 'baby', 'girl', 'xxx', 'booty']
def filter_terms(terms):
        filtered_terms = []
        for term in terms:
            is_filtered = False
            if len(term)  > 4 and '..' not in term:
                #is_filtered = False
                for stop_term in stop_terms:
                    if stop_term in term:
                        is_filtered = True #filtered_terms.append(term)
                    #else:
                    #    print('removed', term)
            if not is_filtered:
                filtered_terms.append(term)
        return filtered_terms           


def get_new_search_terms(text_clf_svm, tag_tweets, time_taken, ucb_cost_value_estimator, mean_cost_value_estimator, mean_10_cost_value_estimator):
    
        tag_values_update = get_tag_values_and_count(tag_tweets, time_taken)
        
        print('tag_values_update: ', tag_values_update)
        
        ucb_cost_value_estimator.update_tag_queue( tag_values_update.copy())
        ucb_knapsack_terms, ucb_cost_value = ucb_cost_value_estimator.get_ucb_estimate()
        
        mean_cost_value_estimator.update_tag_queue( tag_values_update.copy())
        mean_knapsack_terms, mean_cost_value  = mean_cost_value_estimator.get_cost_value_based_on_mean_value()
    
        
        mean_10_cost_value_estimator.update_tag_queue( tag_values_update.copy())
        mean_10_knapsack_terms, mean_10_cost_value  = mean_10_cost_value_estimator.get_cost_value_based_on_mean_value()

        
        ucb_next_search_terms = knapsack_solver(ucb_cost_value, ucb_knapsack_terms)
        mean_next_search_terms = knapsack_solver(mean_cost_value, mean_knapsack_terms)
        mean_10_next_search_terms = knapsack_solver(mean_10_cost_value, mean_10_knapsack_terms)

        print('ucb_next_search_terms: ', ucb_next_search_terms)
        print('mean_next_search_terms: ', mean_next_search_terms)
        print('mean_10_next_search_terms: ', mean_10_next_search_terms)
        
        time_now = datetime.now()
        with open('./ucb_next_search_terms.txt', 'a') as f_write:
            f_write.write(('{}\t{}\n').format(str(time_now), json.dumps(ucb_next_search_terms)))
            
        with open('./mean_next_search_terms.txt', 'a') as f_write:
            f_write.write(('{}\t{}\n').format(str(time_now), json.dumps(mean_next_search_terms)))
        
        with open('./mean_10_next_search_terms.txt', 'a') as f_write:
            f_write.write(('{}\t{}\n').format(str(time_now), json.dumps(mean_10_next_search_terms)))

            
        # For comparision, let's join them assuming it does exceed the Twitter threshod
        # This is only true for search with less commonly used terms like `earthquake'
        # Ideally wll these should be separate processes
      
        suggested_search_terms = ucb_next_search_terms + mean_next_search_terms + mean_10_next_search_terms
        if len(suggested_search_terms) > 0:
            search_terms = list(set(earthquake_terms.copy() + filter_terms(suggested_search_terms)))
        else:
            search_terms = earthquake_terms.copy()
            
        return search_terms