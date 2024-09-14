import pickle
import os
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import logging

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_tweets(filename='whole_archive_tweets.pkl'):
    tweets_filepath = os.path.join('data', filename)
    try:
        with open(tweets_filepath, 'rb') as f:
            tweets = pickle.load(f)
        logging.info(f"Loaded {len(tweets)} tweets from {tweets_filepath}")
        return tweets
    except FileNotFoundError:
        logging.error(f"File not found: {tweets_filepath}")
        return []

def calculate_keyword_stats(tweets):
    stop_words = set(stopwords.words('english'))
    word_counts = Counter()

    for tweet in tweets:
        words = word_tokenize(tweet['full_text'].lower())
        words = [word for word in words if word.isalnum() and word not in stop_words]
        word_counts.update(words)

    return word_counts

def save_keyword_stats(word_counts, filename='keyword_stats.pkl'):
    output_filepath = os.path.join('data', filename)
    with open(output_filepath, 'wb') as f:
        pickle.dump(word_counts, f)
    logging.info(f"Saved keyword stats to {output_filepath}")

def keyword_stats_main(args):
    logging.info("Running Keyword Stats Analysis with args: %s", args)

    all_tweets = load_tweets(args.input) if args.input else load_tweets()
    
    if not all_tweets:
        logging.error("No tweets loaded. Unable to perform analysis.")
        return

    logging.info("Total tweets loaded: %d", len(all_tweets))

    word_counts = calculate_keyword_stats(all_tweets)
    save_keyword_stats(word_counts)

    logging.info("Keyword stats calculation and saving complete.")
