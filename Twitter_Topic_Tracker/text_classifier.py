import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV



def clean_tweet(text):
    text= text.lower().replace('nepal', ' ')    
    return text


def get_data(df):
	relevant_tweets = []
	non_relavant_tweets = []

	for text, label in zip(df['text'], df['label']):
		if label == 'relevant':
			relevant_tweets.append(clean_tweet(text))
		else:
			non_relavant_tweets.append(clean_tweet(text))

	print('relevant_tweets: ', len(relevant_tweets))        
	print('non_relavant_tweets: ', len(non_relavant_tweets))   

	return relevant_tweets, non_relavant_tweets

def get_trained_classifier(acl_tweetsPath):

	df_nepal_train = pd.read_csv(acl_tweetsPath+ "2015_Nepal_Earthquake_train.tsv", sep = '\t', encoding='latin1')
	print(len(df_nepal_train['label']))

	df_nepal_test = pd.read_csv(acl_tweetsPath+ "2015_Nepal_Earthquake_test.tsv", sep = '\t', encoding='latin1')
	print(len(df_nepal_test))

	df_nepal_dev = pd.read_csv(acl_tweetsPath+ "2015_Nepal_Earthquake_dev.tsv", sep = '\t', encoding='latin1')
	print(len(df_nepal_dev))


	print(len(set(df_nepal_train['label'])))

	label_set = list(set(df_nepal_train['label']))
	print(label_set)



	train_relevant_tweets, train_non_relavant_tweets = get_data(df_nepal_train)
	test_relevant_tweets, test_non_relavant_tweets = get_data(df_nepal_test)

	parameters_svm = {'vect__ngram_range': [(1, 1), (1, 2)], 
	                  'tfidf__use_idf': (True, False),
	                  'clf-svm__alpha': (1e-2, 1e-3),
	                 }


	text_pipeline_nb = Pipeline([('vect', CountVectorizer()),
	                     ('tfidf', TfidfTransformer()),
	                    ('clf', MultinomialNB())])

	text_clf_svm = Pipeline([('vect', CountVectorizer()),
	                         ('tfidf', TfidfTransformer()),
	                         ('clf-svm', SGDClassifier(loss='hinge', penalty='l2',
	                                                   alpha=1e-3, max_iter=5, random_state=42)),
	                        ])


	text_clf_svm.fit(train_relevant_tweets + train_non_relavant_tweets,                  [1]*len(train_relevant_tweets) + [0]*len(train_non_relavant_tweets) )
	predicted = text_clf_svm.predict(test_relevant_tweets + test_non_relavant_tweets)

	print(np.mean(predicted == [1]*len(test_relevant_tweets) + [0]*len(test_non_relavant_tweets)))

	return text_clf_svm