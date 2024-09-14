import logging
from collections import Counter
import logging
from dateutil.parser import parse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UserStats:
    def __init__(self, tweets):
        self.user_tweets = tweets

    def get_user_stats(self, username):

        total_tweets = len(self.user_tweets)
        total_likes = sum(tweet['favorite_count'] for tweet in self.user_tweets)
        total_retweets = sum(tweet['retweet_count'] for tweet in self.user_tweets)
        total_replies = sum(1 for tweet in self.user_tweets if tweet['reply_to_tweet_id'] is not None)

        first_tweet_date = min(parse(tweet['created_at']) for tweet in self.user_tweets)
        last_tweet_date = max(parse(tweet['created_at']) for tweet in self.user_tweets)

        date_range = (last_tweet_date - first_tweet_date).days + 1
        weeks = date_range / 7

        # Calculate most active hours and days
        hour_counts = Counter(parse(tweet['created_at']).hour for tweet in self.user_tweets)
        day_counts = Counter(parse(tweet['created_at']).strftime('%A') for tweet in self.user_tweets)
        most_active_hours = sorted(hour_counts, key=hour_counts.get, reverse=True)[:3]
        most_active_days = sorted(day_counts, key=day_counts.get, reverse=True)[:3]

        return {
            'username': username,
            'total_tweets': total_tweets,
            'total_likes': total_likes,
            'total_retweets': total_retweets,
            'total_replies': total_replies,
            'avg_tweets_per_day': total_tweets / date_range if date_range > 0 else 0,
            'avg_tweets_per_week': total_tweets / weeks if weeks > 0 else 0,
            'avg_likes_per_tweet': total_likes / total_tweets if total_tweets > 0 else 0,
            'avg_retweets_per_tweet': total_retweets / total_tweets if total_tweets > 0 else 0,
            'avg_replies_per_tweet': total_replies / total_tweets if total_tweets > 0 else 0,
            'first_tweet_date': first_tweet_date,
            'last_tweet_date': last_tweet_date,
            'most_active_hours': most_active_hours,
            'most_active_days': most_active_days
        }

    def print_user_stats(self, stats):
        logger.info(f"Stats for @{stats['username']}:")
        logger.info(f"Total tweets analyzed: {stats['total_tweets']}")
        logger.info(f"Total likes received: {stats['total_likes']}")
        logger.info(f"Total retweets: {stats['total_retweets']}")
        logger.info(f"Total replies: {stats['total_replies']}")
        logger.info(f"Average tweets per day: {stats['avg_tweets_per_day']:.2f}")
        logger.info(f"Average tweets per week: {stats['avg_tweets_per_week']:.2f}")
        logger.info(f"Average likes per tweet: {stats['avg_likes_per_tweet']:.2f}")
        logger.info(f"Average retweets per tweet: {stats['avg_retweets_per_tweet']:.2f}")
        logger.info(f"Average replies per tweet: {stats['avg_replies_per_tweet']:.2f}")
        logger.info(f"Most active hours: {', '.join(map(str, stats['most_active_hours']))}")
        logger.info(f"Most active days: {', '.join(stats['most_active_days'])}")
        logger.info(f"First tweet date: {stats['first_tweet_date']}")
        logger.info(f"Last tweet date: {stats['last_tweet_date']}")

    def print_sample_data(self):
        if self.tweets:
            logger.info("Sample Tweet:")
            logger.info(str(self.tweets[0]))
        else:
            logger.warning("No tweets available to display as sample.")


def user_stats_main(args, tweets_dict):
    try:
        user_tweets = tweets_dict[args.usernames[0]]
        user_stats = UserStats(user_tweets)

        stats = user_stats.get_user_stats(args.usernames[0])
        if stats:
            user_stats.print_user_stats(stats)  # Keep this for console logging
            return stats
        else:
            logger.warning(f"Error calculating stats for user: {args.usernames[0]}")
            return None

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return None
