# API configurations
SUPABASE_URL = 'https://fabxmporizzqflnftavs.supabase.co/'

import os

# File paths
DATA_DIR = 'data'
OUTPUT_DIR = 'output'
TWEET_GRAPH_FILE = os.path.join(DATA_DIR, 'tweet_graph.pkl')
ACCOUNTS_FILE = os.path.join(DATA_DIR, 'accounts.pkl')
TWEETS_FILE = os.path.join(DATA_DIR, 'whole_archive_tweets.pkl')
INTERESTING_SUBGRAPHS_FILE = os.path.join(DATA_DIR, 'interesting_subgraphs.pkl')

# NRC Lexicon file path
NRC_LEXICON_FILE = 'sentiment_analysis/NRC-Emotion-Lexicon-Wordlevel-v0.92.txt'

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
