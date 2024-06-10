import streamlit as st
import requests
import json

# Constants for each model's API endpoint and headers
OPENAI_API_URL = "https://api.openai.com/v1/images/generations"
OPENAI_HEADERS = {
    "Authorization": f"Bearer {st.secrets['openai_api_key']}",  # Use st.secrets for OpenAI API key
    "Content-Type": "application/json",
}

DEEPINFRA_API_URL = "https://api.deepinfra.com/v1/inference/stability-ai/sdxl?version=28fb12be4e4d05ff054e10eabd20e429efb98293056db1067ccdbb8ac2733b86"
DEEPINFRA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Accept-Language": "en-PH,en-US;q=0.9,en;q=0.8",
    "Origin": "https://deepinfra.com",
    "Referer": "https://deepinfra.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": "Android"
}

# Streamlit page config
st.set_page_config(
    page_title="Lumiere",
    page_icon="🖼️",
    layout="centered",
)

# Hide main menu and footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("Lumiere")

# Session state to maintain data
if 'model' not in st.session_state:
    st.session_state.model = "dall-e-2"
if 'prompt' not in st.session_state:
    st.session_state.prompt = "A cute baby sea otter"
if 'image_count' not in st.session_state:
    st.session_state.image_count = 4
if 'image_size' not in st.session_state:
    st.session_state.image_size = "1024x1024"

# Function to reset settings
def reset_settings():
    st.session_state.model = "dall-e-2"
    st.session_state.prompt = "A cute baby sea otter"
    st.session_state.image_count = 4
    st.session_state.image_size = "1024x1024"

# Dropdown for model selection
st.session_state.model = st.selectbox(
    "Select the AI model:",
    ("dall-e-2", "dall-e-3", "sdxl"),
    index=["dall-e-2", "dall-e-3", "sdxl"].index(st.session_state.model)
)

# User input for text prompt
st.session_state.prompt = st.text_input("Enter a text prompt:", st.session_state.prompt)

# Settings for OpenAI models
if st.session_state.model in ["dall-e-2", "dall-e-3"]:
    st.session_state.image_count = 1 if st.session_state.model == "dall-e-3" else st.number_input("Number of images", min_value=1, max_value=4, value=st.session_state.image_count, step=1)
    st.session_state.image_size = st.selectbox("Image size", ["256x256", "512x512", "1024x1024"] if st.session_state.model == "dall-e-2" else ["1024x1024", "1792x1024", "1024x1792"])

# Settings for DeepInfra model
elif st.session_state.model == "sdxl":
    st.session_state.image_count = st.number_input("Number of images", min_value=1, max_value=4, value=st.session_state.image_count, step=1)

# Let's use containers for better layout handling
reset_button_container = st.container()
generate_button_container = st.container()
image_display_container = st.container()

# Reset button
with reset_button_container:
    if st.button("🔄"):
        reset_settings()
        st.experimental_rerun()

# Button to trigger image generation
with generate_button_container:
    if st.button("Generate"):
        with st.spinner(""):
            if st.session_state.model in ["dall-e-2", "dall-e-3"]:
                # OpenAI Models
                max_length = 4000 if st.session_state.model == "dall-e-3" else 1000
                if len(st.session_state.prompt) > max_length:
                    st.error(f"Prompt is too long. Maximum length for {st.session_state.model} is {max_length} characters.")
                else:
                    # Data for the POST request
                    data = {
                        "model": st.session_state.model,
                        "prompt": st.session_state.prompt,
                        "n": st.session_state.image_count if st.session_state.model != "dall-e-3" else 1,
                        "size": st.session_state.image_size
                    }

                    # Make the POST request
                    response = requests.post(OPENAI_API_URL, headers=OPENAI_HEADERS, data=json.dumps(data))

                    # Check if the response status code is 200 (OK)
                    if response.status_code == 200:
                        result = response.json()
                        if "data" in result and len(result["data"]) > 0:
                            images_per_row = 2
                            cols = image_display_container.columns(images_per_row)
                            for i, image_obj in enumerate(result["data"]):
                                image_url = image_obj["url"]
                                with cols[i % images_per_row]:
                                    st.image(image_url)
                        else:
                            st.error("No images returned from the API.")
                    else:
                        st.error("Failed to generate the images, please try again.")

            elif st.session_state.model == "sdxl":
                # DeepInfra Model
                data = {
                    "input": {
                        "prompt": st.session_state.prompt,
                        "num_outputs": st.session_state.image_count,  # Generate specified number of images
                        "width": 1024,  # Fixed size for sdxl model
                        "height": 1024
                    }
                }

                # Make the POST request
                response = requests.post(DEEPINFRA_API_URL, headers=DEEPINFRA_HEADERS, data=json.dumps(data))

                # Check if the response status code is 200 (OK)
                if response.status_code == 200:
                    result = response.json()
                    if "output" in result and len(result["output"]) > 0:
                        images_per_row = 2
                        cols = image_display_container.columns(images_per_row)
                        for i, image_url in enumerate(result["output"]):
                            with cols[i % images_per_row]:
                                st.image(image_url)
                    else:
                        st.error("No images returned from the API.")
                else:
                    st.error("Failed to generate the images, please try again.")
