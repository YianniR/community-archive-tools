import streamlit as st
from datetime import datetime, timedelta, date
from sentiment_analysis.mood import sentiment_analysis_main
from common.fetch_data import fetch_data_main
from common.layout import set_page_config, common_layout, display_error, save_plot_as_image, create_download_button

def main():
    set_page_config("Sentiment Analysis", "😊")
    common_layout("Sentiment Analysis", "Analyze the sentiment of tweets over time.")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    date_range = st.date_input("Select date range", value=(start_date, end_date), max_value=end_date)

    username = st.text_input('Twitter username')
    ma_window = st.number_input('Moving average window size', min_value=1, max_value=365, value=30)

    # Add checkboxes for emotion dimensions
    st.subheader("Select emotion dimensions to display:")
    emotion_dimensions = ['anger', 'fear', 'anticipation', 'trust', 'surprise', 'sadness', 'joy', 'disgust']
    selected_emotions = {emotion: st.checkbox(emotion.capitalize(), value=True) for emotion in emotion_dimensions}

    if st.button('Analyze'):
        if len(date_range) == 2:
            start_date, end_date = date_range
            days = (end_date - start_date).days
        else:
            st.error("Please select both start and end dates.")
            return

        args = type('Args', (), {
            'start_date': start_date,
            'end_date': end_date,
            'usernames': [username],
            'ma_window': int(ma_window),
        })()

        with st.spinner('Analyzing sentiment...'):
            tweets_dict = fetch_data_main(args)
            if tweets_dict:
                fig = sentiment_analysis_main(args, tweets_dict, selected_emotions)
            else:
                display_error(f'Failed to find user in database. Check capitalisation & spelling?')
                return

        if fig:
            st.subheader("Sentiment Analysis Results")
            st.plotly_chart(fig, use_container_width=True)
            
            # Save the figure as a PNG file
            output_filename = f'sentiment_analysis_{username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            output_path = save_plot_as_image(fig, output_filename)
            
            if output_path:
                create_download_button(output_path, "Download PNG")
            else:
                display_error(f'Failed to generate the image file.')
        else:
            display_error('Failed to generate the analysis. Please check the logs for more information.')

if __name__ == '__main__':
    main()
