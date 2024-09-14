import streamlit as st
from common.layout import set_page_config

def main():
    set_page_config("Community Archive Analysis Tool", "📊")

    # st.sidebar.markdown(
    #     "[View on GitHub](https://github.com/YianniR/community-archive-scripts)",
    #     unsafe_allow_html=True
    # )

    st.markdown("""
    <h1 style='text-align: center;'>Community Archive Analysis Tool</h1>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style='text-align: center;'>
    This project uses data from the <a href="http://www.community-archive.org">Community Archive</a> project. 
    </p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <a href='/User_Statistics' target='_self'>
            <div style='background-color: #17BF63; padding: 20px; border-radius: 10px; text-align: center;'>
                <h3 style='color: white;'>👤 User Statistics</h3>
                <p style='color: white;'>Generate user-specific statistics</p>
            </div>
        </a>
        """, unsafe_allow_html=True)
            
    with col2:
        st.markdown("""
        <a href='/Sentiment_Analysis' target='_self'>
            <div style='background-color: #F45D22; padding: 20px; border-radius: 10px; text-align: center;'>
                <h3 style='color: white;'>😊 Sentiment Analysis</h3>
                <p style='color: white;'>Analyze tweet sentiments over time</p>
            </div>
        </a>
        """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
