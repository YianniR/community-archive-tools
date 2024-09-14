import streamlit as st
from thread_explorer.thread_explorer_main import thread_explorer_main
from common.layout import set_page_config, common_layout, display_error

def main():
    set_page_config("Thread Explorer", "🧵")
    common_layout("Thread Explorer", "Visualize and analyze tweet threads.")

    method = st.selectbox('Select method', ['size', 'branching'])
    num_subgraphs = st.number_input('Number of subgraphs to display', min_value=1, max_value=20, value=5)

    if st.button('Explore Threads'):
        args = type('Args', (), {
            'method': method, 
            'num_subgraphs': int(num_subgraphs)
        })()

        with st.spinner('Exploring threads...'):
            fig = thread_explorer_main(args)

        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            display_error('Failed to generate the visualization. Please check the logs for more information.')

if __name__ == '__main__':
    main()
