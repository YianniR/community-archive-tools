import pickle
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, date
import logging
from dateutil.parser import parse
from dateutil.tz import tzutc
import os
from collections import Counter
import time
from functools import wraps

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} took {end_time - start_time:.2f} seconds to execute.")
        return result
    return wrapper

@timing_decorator
def load_tweets(filename='whole_archive_tweets.pkl', accounts_filename='accounts.pkl'):
    tweets_filepath = os.path.join('data', filename)
    accounts_filepath = os.path.join('data', accounts_filename)
    
    with open(tweets_filepath, 'rb') as f:
        tweets = pickle.load(f)
    logging.info(f"Loaded {len(tweets)} tweets from {tweets_filepath}")
    
    with open(accounts_filepath, 'rb') as f:
        accounts = pickle.load(f)
    
    account_map = {str(account['account_id']): account['username'] for account in accounts}

    for tweet in tweets:
        tweet['username'] = account_map.get(str(tweet['account_id']), f"Unknown (ID: {tweet['account_id']})")
    
    return tweets

@timing_decorator
def filter_tweets_by_date(tweets, start_date, end_date, username=None):
    filtered_tweets = [
        tweet for tweet in tweets
        if start_date <= parse(tweet['created_at']).replace(tzinfo=tzutc()) <= end_date
        and (username is None or tweet['username'].lower() == username.lower())
    ]
    
    logging.info(f"Filtered {len(filtered_tweets)} tweets between {start_date} and {end_date}")
    return filtered_tweets

@timing_decorator
def count_keywords(tweets, keywords):
    keyword_counts = {keyword: Counter() for keyword in keywords}
    dates = set()

    for tweet in tweets:
        tweet_date = parse(tweet['created_at']).date()
        tweet_text = tweet['full_text'].lower()
        
        dates.add(tweet_date)
        for keyword in keywords:
            if keyword.lower() in tweet_text:
                keyword_counts[keyword][tweet_date] += 1

    dates = sorted(dates)
    return dates, {k: [v[d] for d in dates] for k, v in keyword_counts.items()}

@timing_decorator
def plot_keyword_trends(dates, keyword_counts, ma_window=1, username=None, keywords=None):
    fig = make_subplots(rows=1, cols=1)
    
    for keyword, counts in keyword_counts.items():
        # Calculate moving average
        ma_counts = pd.Series(counts).rolling(window=ma_window, center=True).mean()
        fig.add_trace(go.Scatter(x=dates, y=ma_counts, mode='lines', name=keyword))

    fig.update_layout(
        title=f"Keyword Trends {'for @' + username if username else ''}",
        xaxis_title="Date",
        yaxis_title="Keyword Count",
        legend_title="Keywords",
        height=600,
        width=1000
    )

    # Create filename with keywords
    keywords_str = '_'.join(keywords) if keywords else 'keywords'
    filename = f'keyword_trends_{keywords_str}{"_" + username if username else ""}.html'
    output_filename = os.path.join('output', filename)
    fig.write_html(output_filename)
    logging.info(f"Keyword trends plot saved as '{output_filename}'")
    
    return output_filename, fig

@timing_decorator
def keyword_trends_main(args, progress_callback=None):
    logging.info("Running Keyword Trends Analysis with args: %s", args)
    
    all_tweets = load_tweets(args.input) if args.input else load_tweets()
    logging.info("Total tweets loaded: %d", len(all_tweets))
    
    if progress_callback:
        progress_callback(0.2)
    
    end_date = datetime.now(tzutc())
    start_date = end_date - timedelta(days=args.days)
    
    filtered_tweets = filter_tweets_by_date(all_tweets, start_date, end_date, args.username)
    logging.info("Tweets within date range: %d", len(filtered_tweets))
    
    if progress_callback:
        progress_callback(0.4)
    
    if args.username:
        tweet_count = len(filtered_tweets)
        logging.info("Tweets for username '%s': %d", args.username, tweet_count)
        print(f"Found {tweet_count} tweets for user @{args.username}")
        if not filtered_tweets:
            logging.warning("No tweets found for username: %s", args.username)
            return None, None
    
    if filtered_tweets:
        keywords = args.keywords.split(',')
        dates, keyword_counts = count_keywords(filtered_tweets, keywords)
        
        if progress_callback:
            progress_callback(0.6)
        
        output_filename, fig = plot_keyword_trends(dates, keyword_counts, ma_window=args.ma_window, username=args.username, keywords=keywords)
        
        if progress_callback:
            progress_callback(1.0)
        
        logging.info("Keyword trends analysis complete. Check the generated %s file.", output_filename)
        return output_filename, fig
    else:
        logging.warning("No tweets found in the specified date range or for the given username.")
        return None, None
