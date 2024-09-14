import streamlit as st

def set_page_config(title, icon):
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")

def common_layout(title, description):
    st.title(title)
    st.write(description)

def display_error(message):
    st.error(message)

def display_success(message):
    st.success(message)

def display_info(message):
    st.info(message)

def display_image(image_path, caption=None):
    st.image(image_path, caption=caption)

import os
from io import BytesIO
import plotly.io as pio

def create_download_button(file_path, button_text):
    with open(file_path, "rb") as file:
        file_data = file.read()
    file_name = os.path.basename(file_path)
    mime_type = "image/png"
    st.download_button(
        label=button_text,
        data=file_data,
        file_name=file_name,
        mime=mime_type
    )

def save_plot_as_image(fig, filename):
    img_bytes = pio.to_image(fig, format="png")
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    with open(output_path, "wb") as f:
        f.write(img_bytes)
    return output_path
