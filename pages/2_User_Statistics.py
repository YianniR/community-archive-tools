import streamlit as st
from user_stats.user_stats_main import user_stats_main
from common.fetch_data import fetch_data_main
from common.layout import set_page_config, common_layout, display_error

def format_date(date):
    return date.strftime("%Y-%m-%d %H:%M:%S UTC")

def main():
    set_page_config("User Statistics", "👤")
    common_layout("User Statistics", "Generate statistics for individual Twitter users.")

    username = st.text_input('Enter Twitter username')
    
    if st.button('Generate Statistics'):
        if not username:
            display_error('Please enter a username.')
            return

        args = type('Args', (), {
            'usernames': [username],
            'start_date': None,
            'end_date': None
        })()

        with st.spinner('Generating user statistics...'):
            tweets_dict = fetch_data_main(args)
            if tweets_dict:
                stats = user_stats_main(args, tweets_dict)
            else:
                display_error(f'Failed to find user in database. Check capitalisation & spelling?')
                return
             
        if stats:
            st.header(f"Statistics for @{stats['username']}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("General Information")
                st.write(f"Total tweets: {stats['total_tweets']:,}")
                st.write(f"First tweet: {format_date(stats['first_tweet_date'])}")
                st.write(f"Last tweet: {format_date(stats['last_tweet_date'])}")
            
            with col2:
                st.subheader("Tweet Statistics")
                st.write(f"Average tweets per day: {stats['avg_tweets_per_day']:.2f}")
                st.write(f"Average tweets per week: {stats['avg_tweets_per_week']:.2f}")
                st.write(f"Total likes received: {stats['total_likes']:,}")
                st.write(f"Total retweets: {stats['total_retweets']:,}")
            
            with col3:
                st.subheader("Engagement Metrics")
                st.write(f"Average likes per tweet: {stats['avg_likes_per_tweet']:.2f}")
                st.write(f"Average retweets per tweet: {stats['avg_retweets_per_tweet']:.2f}")
                st.write(f"Average replies per tweet: {stats['avg_replies_per_tweet']:.2f}")
            
            st.subheader("Most Active Hours")
            active_hours = ", ".join([f"{hour}:00" for hour in stats['most_active_hours']])
            st.write(active_hours)

            st.subheader("Most Active Days")
            active_days = ", ".join(stats['most_active_days'])
            st.write(active_days)

        else:
            display_error(f"No statistics found for user @{username}. The user might not exist or have no tweets in the dataset.")

if __name__ == '__main__':
    main()
