import streamlit as st
import pickle
import os
from common.layout import set_page_config, common_layout, display_info

def load_keyword_stats(filename='keyword_stats.pkl'):
    filepath = os.path.join('data', filename)
    try:
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        st.error(f"Keyword stats file not found: {filepath}")
        return None

def main():
    set_page_config("Keyword Statistics", "🔑")
    common_layout("Keyword Statistics", "Explore the frequency of keywords in tweets.")

    word_counts = load_keyword_stats()
    
    if word_counts is None:
        return

    search_term = st.text_input("Search for a keyword (optional):")
    
    if search_term:
        matching_words = [word for word in word_counts.keys() if search_term.lower() in word.lower()]
        matching_words.sort(key=lambda x: word_counts[x], reverse=True)
        
        if matching_words:
            st.subheader(f"Matching Keywords (Top 5000):")
            data = [(word, word_counts[word]) for word in matching_words[:5000]]
            st.table(data)
        else:
            st.info("No matching keywords found.")
    else:
        st.subheader("Top 5000 Keywords:")
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5000]
        st.table(top_words)

if __name__ == '__main__':
    main()
