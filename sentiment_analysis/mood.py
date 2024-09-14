import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import logging
import nltk
from nltk.tokenize import word_tokenize
import os
from dateutil.parser import parse

import multiprocessing
import time
from joblib import Memory

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up caching
cache_dir = '.cache'
memory = Memory(cache_dir, verbose=0)

from functools import lru_cache, wraps

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"{func.__name__} took {end_time - start_time:.2f} seconds to execute.")
        return result
    return wrapper

# Initialize VADER sentiment analyzer
sia = SentimentIntensityAnalyzer()

@lru_cache(maxsize=10000)
def sentiment_analyzer(text):
    return [{'score': sia.polarity_scores(text)['compound']}]

# Download necessary NLTK data
nltk.download('punkt_tab', quiet=True)

from config import NRC_LEXICON_FILE

def load_nrc_lexicon(file_path=NRC_LEXICON_FILE):
    emotion_lexicon = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                word, emotion, value = line.strip().split('\t')
                if int(value) == 1:
                    if word not in emotion_lexicon:
                        emotion_lexicon[word] = []
                    emotion_lexicon[word].append(emotion)
    else:
        logging.warning(f"NRC Lexicon file not found: {file_path}")
    return emotion_lexicon

emotion_lexicon = load_nrc_lexicon()

def analyze_emotions(text):
    words = pd.Series(word_tokenize(text.lower()))
    emotions = words.map(emotion_lexicon).explode()
    emotion_counts = emotions.value_counts()
    total = emotion_counts.sum()
    
    if total > 0:
        return emotion_counts.div(total).to_dict()
    else:
        return {emotion: 0 for emotion in ['anger', 'fear', 'anticipation', 'trust', 'surprise', 'sadness', 'joy', 'disgust']}

def process_single_tweet(tweet):
    sentiment = sentiment_analyzer(tweet['full_text'])[0]['score']
    emotions = analyze_emotions(tweet['full_text'])
    
    # Handle both string and Timestamp types for created_at
    if isinstance(tweet['created_at'], str):
        created_at = parse(tweet['created_at'])
    else:
        created_at = tweet['created_at']
    
    return {
        'created_at': created_at,
        'sentiment': sentiment,
        **emotions
    }

@timing_decorator
def process_tweets(tweets):
    with multiprocessing.Pool() as pool:
        data = pool.map(process_single_tweet, tweets)
    
    return pd.DataFrame(data)

@memory.cache
def cached_process_tweets(tweets):
    return process_tweets(tweets)

@timing_decorator
def aggregate_mood(df, freq='D'):
    aggregated = df.set_index('created_at').resample(freq).mean()
    logging.info(f"Aggregated mood data shape: {aggregated.shape}")
    logging.info(f"Aggregated mood data date range: {aggregated.index.min()} to {aggregated.index.max()}")
    
    # Count non-NaN values for each day
    non_nan_counts = aggregated.notna().sum(axis=1)
    days_with_data = non_nan_counts[non_nan_counts > 0]
    logging.info(f"Days with data: {len(days_with_data)} out of {len(aggregated)}")
    
    # Log information about days without data
    days_without_data = non_nan_counts[non_nan_counts == 0]
    if not days_without_data.empty:
        logging.info(f"Days without data: {len(days_without_data)}")
        logging.info(f"First day without data: {days_without_data.index[0]}")
        logging.info(f"Last day without data: {days_without_data.index[-1]}")
    
    return aggregated

def calculate_moving_average(data, window):
    return data.rolling(window=window, min_periods=1).mean()

def assign_emotion_colors(emotions):
    # Hardcoded color mapping for emotions
    # Colors are in RGB format (0-255 for each channel)
    emotion_color_dict = {
        'anger': (1.0, 0.0, 0.0),      # Red
        'fear': (0.5, 0.0, 0.5),       # Purple
        'anticipation': (1.0, 0.65, 0.0),  # Orange
        'trust': (0.0, 1.0, 0.0),      # Green
        'surprise': (0.0, 1.0, 1.0),   # Cyan
        'sadness': (0.0, 0.0, 1.0),    # Blue
        'joy': (1.0, 0.75, 0.8),       # Pink
        'disgust': (0.65, 0.16, 0.16)  # Brown
    }
    
    # Assign colors to the input emotions
    colors = [emotion_color_dict.get(emotion, (0.5, 0.5, 0.5)) for emotion in emotions]
    
    
    return colors

@timing_decorator
def plot_mood_meter(mood_data, ma_window=1, username=None, start_date=None, end_date=None, selected_emotions=None):
    logging.info(f"Starting plot_mood_meter function with {len(mood_data)} data points")
    print(f"mood_data shape: {mood_data.shape}")
    print(f"mood_data index: {mood_data.index}")
    print(f"mood_data columns: {mood_data.columns}")
    print(f"selected_emotions: {selected_emotions}")
    
    emotions = [col for col in mood_data.columns if col != 'sentiment' and (selected_emotions is None or selected_emotions.get(col, False))]
    colors = assign_emotion_colors(emotions)

    fig = make_subplots(rows=2, cols=1, subplot_titles=('Overall Sentiment', 'Emotional Dimensions'))
    
    # Ensure the index is in datetime format
    mood_data.index = pd.to_datetime(mood_data.index)
    print(f"mood_data index after conversion: {mood_data.index}")
    
    # Set x-axis range
    x_range = [mood_data.index.min(), mood_data.index.max()]
    
    # Plot sentiment
    if 'sentiment' in mood_data.columns:
        sentiment_ma = calculate_moving_average(mood_data['sentiment'], ma_window)
        fig.add_trace(
            go.Scatter(x=mood_data.index, y=sentiment_ma, mode='lines', name=f'Sentiment ({ma_window}-day MA)',
                       line=dict(color='black', width=2)),
            row=1, col=1
        )
        fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=1)
        logging.info(f"Sentiment plot created with {len(sentiment_ma)} points")
    else:
        logging.warning("No 'sentiment' column found in mood_data")
    
    # Plot emotions
    for emotion, color in zip(emotions, colors):
        print(emotion, color)
        if emotion in mood_data.columns:
            emotion_ma = calculate_moving_average(mood_data[emotion], ma_window)
            fig.add_trace(
                go.Scatter(x=mood_data.index, y=emotion_ma, mode='lines', name=f'{emotion.capitalize()} ({ma_window}-day MA)',
                           line=dict(color=f'rgb{tuple(int(c*255) for c in color)}', width=2)),
                row=2, col=1
            )
            logging.info(f"Plotted {emotion} with {len(emotion_ma)} points")
        else:
            logging.warning(f"No '{emotion}' column found in mood_data")
    
    # Update x-axis range for both subplots
    fig.update_xaxes(range=x_range, row=1, col=1)
    fig.update_xaxes(range=x_range, row=2, col=1)
    
    # Update layout
    title = f'Mood Meter Analysis: {ma_window}-Day Moving Average'
    if username:
        title += f' for @{username}'
    if start_date and end_date:
        title += f'\nDate Range: {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}'
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            y=0.95,
            xanchor='center',
            yanchor='top'
        ),
        height=900,  # Increased height to accommodate legend below
        width=1000,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    fig.update_xaxes(title_text="Date", row=2, col=1, type='date')
    fig.update_yaxes(title_text="Sentiment (-1 to 1)", row=1, col=1)
    fig.update_yaxes(title_text="Emotion Intensity (0 to 1)", row=2, col=1)
    
    # Add annotations
    fig.add_annotation(
        text="Positive",
        xref="paper", yref="y",
        x=1.02, y=0.75,
        showarrow=False,
        row=1, col=1
    )
    fig.add_annotation(
        text="Negative",
        xref="paper", yref="y",
        x=1.02, y=-0.75,
        showarrow=False,
        row=1, col=1
    )
    
    logging.info("Plotly figure created successfully")
    return fig

@timing_decorator
def sentiment_analysis_main(args, tweets_dict, selected_emotions=None):
    logging.info("Running Sentiment Analysis with args: %s", args)
    logging.info("Selected emotions: %s", selected_emotions)  

    user_tweets = tweets_dict[args.usernames[0]] #hardcode just one username for now
    
    df = cached_process_tweets(tuple(user_tweets))  # Convert list to tuple for caching
    daily_mood = aggregate_mood(df, freq='D')
    daily_mood = daily_mood.dropna()  # Remove rows with NaN values
    
    if daily_mood.empty:
        logging.warning("No valid mood data after aggregation. Unable to generate plot.")
        return None
    
    fig = plot_mood_meter(daily_mood, ma_window=args.ma_window, username=args.usernames[0], start_date=args.start_date, end_date=args.end_date, selected_emotions=selected_emotions)
    logging.info("Sentiment analysis complete.")
    return fig