import argparse
import sys

from common import graph_builder

from common.fetch_data import fetch_data_main
from user_stats.user_stats_main import user_stats_main
from sentiment_analysis.mood import sentiment_analysis_main
from keyword_trends.keyword_trends_main import keyword_trends_main
from keyword_stats.keyword_stats_main import keyword_stats_main
from thread_explorer import thread_explorer_main
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Twitter Data Analysis Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Fetch Data parser
    fetch_data_parser = subparsers.add_parser("fetch_data", help="Fetch account and tweet data for multiple accounts")
    fetch_data_parser.add_argument("usernames", nargs='+', help="Twitter usernames to fetch data for")
    fetch_data_parser.add_argument("--start-date", help="Start date for tweet fetch (YYYY-MM-DD)")
    fetch_data_parser.add_argument("--end-date", help="End date for tweet fetch (YYYY-MM-DD)")

    # Fetch Data parser
    fetch_data_parser = subparsers.add_parser("user_stats", help="Calculate user statistics")
    fetch_data_parser.add_argument("usernames", nargs='+', help="Twitter usernames to fetch data for")

    # Sentiment Analysis parser
    sentiment_parser = subparsers.add_parser("sentiment", help="Run sentiment analysis")
    sentiment_parser.add_argument("usernames", nargs='+', help="Twitter usernames to fetch data for")
    sentiment_parser.add_argument("--start-date", type=str, help="Start date for analysis (YYYY-MM-DD)")
    sentiment_parser.add_argument("--end-date", type=str, help="End date for analysis (YYYY-MM-DD)")
    sentiment_parser.add_argument("--ma-window", type=int, default=7, help="Moving average window size (default: 7)")


    # ------ bellow still WIP

    # Keyword Trends parser
    keyword_parser = subparsers.add_parser("keywords", help="Analyze keyword trends")
    keyword_parser.add_argument("--input", help="Input file name (default: whole_archive_tweets.pkl)")
    keyword_parser.add_argument("--start-date", type=str, help="Start date for analysis (YYYY-MM-DD)")
    keyword_parser.add_argument("--end-date", type=str, help="End date for analysis (YYYY-MM-DD)")
    keyword_parser.add_argument("--username", help="Filter tweets by username")
    keyword_parser.add_argument("--ma-window", type=int, default=7, help="Moving average window size (default: 7)")
    keyword_parser.add_argument("--keywords", required=True, help="Comma-separated list of keywords to analyze")

    # Keyword Stats parser
    keyword_stats_parser = subparsers.add_parser("keyword_stats", help="Calculate keyword statistics")
    keyword_stats_parser.add_argument("--input", help="Input file name (default: whole_archive_tweets.pkl)")
    keyword_stats_parser.add_argument("--top-n", type=int, default=10, help="Number of top keywords to return (default: 10)")

    args = parser.parse_args()

    if args.start_date and args.end_date:
        args.start_date = datetime.strptime(args.start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
        args.end_date = datetime.strptime(args.end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)

    if args.command == "fetch_data":
        fetch_data_main(args)

    elif args.command == "user_stats":
        tweets_dict = fetch_data_main(args)
        if tweets_dict:
            user_stats_main(args, tweets_dict)

    elif args.command == "sentiment":
        tweets_dict = fetch_data_main(args)
        if tweets_dict:
            sentiment_analysis_main(args, tweets_dict)
    
    elif args.command == "keywords":
        keyword_trends_main(args)
    elif args.command == "keyword_stats":
        keyword_stats_main(args)

    elif args.command == "build_graph":
        graph_builder.main(args)
    elif args.command == "visualise_threads":
        thread_explorer_main(args)


    elif args.command == "help":
        if len(sys.argv) > 2:
            subparser_name = sys.argv[2]
            if subparser_name in subparsers.choices:
                subparsers.choices[subparser_name].print_help()
            else:
                print(f"Unknown command: {subparser_name}")
                parser.print_help()
        else:
            parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
