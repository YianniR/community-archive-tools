# fetch_data.py
import time
import os
import logging
from dotenv import load_dotenv
from typing import List, Dict, Optional, Union
from config import SUPABASE_URL, DATA_DIR
from .utils import save_pickle
from dateutil.parser import parse
from datetime import datetime
from supabase import create_client, Client

# Load environment variables and set up logging
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
logging.basicConfig(level=logging.INFO)

class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, API_TOKEN)

class AccountFetcher(SupabaseClient):
    def fetch_batch(self, offset: int = 0, limit: int = 1000) -> List[Dict]:
        try:
            response = self.client.table('account').select('*').range(offset, offset + limit).execute()
            return response.data
        except Exception as e:
            logging.error(f"Error fetching accounts batch: {str(e)}")
            return []

    def fetch_all(self) -> List[Dict]:
        all_accounts = []
        offset = 0
        batch_size = 1000

        while True:
            logging.info(f"Fetching accounts {offset} to {offset + batch_size}...")
            batch = self.fetch_batch(offset, batch_size)
            
            if not batch:
                break
            
            all_accounts.extend(batch)
            offset += batch_size
            
            if len(batch) < batch_size:
                break
            
            time.sleep(0.1)  # To avoid hitting rate limits

        logging.info(f"Total accounts fetched: {len(all_accounts)}")
        return all_accounts

class TweetFetcher(SupabaseClient):
    def fetch_batch(self, account_id: Optional[int] = None, offset: int = 0, limit: int = 5000, 
                    start_date: Optional[datetime] = None, 
                    end_date: Optional[datetime] = None) -> List[Dict]:
        query = self.client.table('tweets').select('*').order('created_at', desc=True).range(offset, offset + limit)
        
        if account_id is not None:
            query = query.eq('account_id', account_id)
        
        if start_date and end_date:
            query = query.gte('created_at', start_date.isoformat()).lte('created_at', end_date.isoformat())

        try:
            logging.info(f"Making request to fetch tweets")
            response = query.execute()
            logging.info(f"Received {len(response.data)} tweets")
            return response.data
        except Exception as e:
            logging.error(f"Error fetching tweets: {str(e)}")
            return []

    def fetch_all(self, account_id: Optional[int] = None, 
                  start_date: Optional[Union[str, datetime]] = None, 
                  end_date: Optional[Union[str, datetime]] = None) -> List[Dict]:
        all_tweets = []
        offset = 0
        batch_size = 5000
   
        while True:
            logging.info(f"Fetching tweets {offset} to {offset + batch_size}...")
            batch = self.fetch_batch(account_id, offset, batch_size, start_date, end_date)
           
            if not batch:
                break
           
            all_tweets.extend(batch)
            offset += batch_size
           
            if len(batch) < batch_size:
                break
           
            time.sleep(0.1)  # To avoid hitting rate limits
   
        logging.info(f"Total tweets fetched: {len(all_tweets)}")
        return all_tweets

def save_data(data: List[Dict], filename: str):
    filepath = os.path.join(DATA_DIR, filename)
    save_pickle(data, filepath)
    logging.info(f"Data saved to {filepath}")

def fetch_data_main(args):
    account_fetcher = AccountFetcher()
    tweet_fetcher = TweetFetcher()

    # Fetch and save accounts
    accounts = account_fetcher.fetch_all()
    if not accounts:
        logging.warning(f"Error fetching accounts.")
        return None

    account_map = {str(account['username']): account['account_id'] for account in accounts}

    tweets_dict = {}
    # Fetch and save tweets for each username
    for username in args.usernames:
        account_id = account_map.get(username)
        if account_id is None:
            logging.warning(f"Unknown username: {username}. Skipping...")
            continue

        logging.info(f"Fetching tweets for {username}")
        user_tweets = tweet_fetcher.fetch_all(account_id, args.start_date, args.end_date)
        logging.info(f"Total tweets for user @{username}: {len(user_tweets)}")

        if not user_tweets:
            logging.warning(f"No tweets found for {username}")
            continue

        # Sort tweets by date in descending order
        user_tweets.sort(key=lambda x: parse(x['created_at']), reverse=True)
        earliest_tweet = min(user_tweets, key=lambda x: parse(x['created_at']))
        latest_tweet = max(user_tweets, key=lambda x: parse(x['created_at']))
        logging.info(f"Earliest tweet date for @{username}: {parse(earliest_tweet['created_at'])}")
        logging.info(f"Latest tweet date for @{username}: {parse(latest_tweet['created_at'])}")

        tweets_dict[username] = user_tweets

    return tweets_dict

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch account and tweet data for multiple accounts")
    parser.add_argument("usernames", nargs='+', help="Twitter usernames to fetch data for")
    parser.add_argument("--start_date", help="Start date for tweet fetch (YYYY-MM-DD)")
    parser.add_argument("--end_date", help="End date for tweet fetch (YYYY-MM-DD)")
    args = parser.parse_args()
    fetch_data_main(args)