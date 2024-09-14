import streamlit as st
from datetime import datetime, timedelta, date
from keyword_trends.keyword_trends_main import keyword_trends_main
from common.layout import set_page_config, common_layout, display_error, save_plot_as_image, create_download_button

def main():
    set_page_config("Keyword Trends Analysis", "📈")
    common_layout("Keyword Trends Analysis", "Analyze keyword trends over time in tweets.")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    date_range = st.date_input("Select date range", value=(start_date, end_date), max_value=end_date)

    username = st.text_input('Twitter username (optional)')
    ma_window = st.number_input('Moving average window size', min_value=1, max_value=365, value=30)
    keywords_input = st.text_input('Enter keywords (comma-separated)', 'tpot,ingroup')
    selected_keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]

    if st.button('Analyze'):
        if not selected_keywords:
            display_error('Please enter at least one keyword.')
            return

        args = type('Args', (), {
            'days': (date_range[1] - date_range[0]).days,
            'username': username if username else None,
            'ma_window': int(ma_window),
            'keywords': ','.join(selected_keywords),
            'input': None
        })()

        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(progress):
            progress_bar.progress(progress)
            status_text.text(f'Analysis progress: {progress:.0%}')

        _, fig = keyword_trends_main(args, progress_callback=progress_callback)

        if fig:
            st.plotly_chart(fig, use_container_width=True)
            
            # Save the figure as a PNG file
            output_filename = f'keyword_trends_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            output_path = save_plot_as_image(fig, output_filename)
            
            if output_path:
                create_download_button(output_path, "Download PNG")
            else:
                display_error(f'Failed to generate the image file.')
        else:
            display_error('Failed to generate the analysis. Please check the logs for more information.')

if __name__ == '__main__':
    main()
