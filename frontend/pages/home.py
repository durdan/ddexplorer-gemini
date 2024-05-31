import streamlit as st
import requests
import time
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv
import os
import vertexai
import re
import joblib
from PIL import Image
from streamlit_navigation_bar import st_navbar
import pages as pg
import base64
from tools.translation import initialize_translation_client, translate_text
import io

# Load environment variables from .env file
def show_home():
    load_dotenv()

    def get_base64(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    
    def set_background(png_file):
        # Load image (ensure correct path and format)
        image = Image.open(png_file).convert('RGB')

        # Encode as base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        bin_str = base64.b64encode(buffered.getvalue()).decode()
        page_bg_img = '''
        <style>
        .stApp {
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
        backdrop-filter: blur(20px) !important;
        }
        </style>
        ''' % bin_str
        st.markdown(page_bg_img, unsafe_allow_html=True)
        
    # set_background('./assets/bg.webp')
    # Backend API URL
    BACKEND_URL = "http://localhost:5000"  # Update with your backend URL
     
    # Replace with your Google Cloud project details
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    location = os.getenv("GEMINI_LOCATION")
   
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    translate_client = initialize_translation_client(GOOGLE_APPLICATION_CREDENTIALS)



    # Define your get_gemini_info function here
    model_name = "gemini-1.0-pro"

    vertexai.init(project=project_id, location=location)
    model = GenerativeModel(model_name=model_name)

    def inject_custom_css():
        with open("./css/stylesheet.css") as f:
            css = f.read()
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

        custom_css = '''
        <style>
        .stTabs [role="tab"] {
            background-color: #f0f0f0;
            color: #333;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 8px 12px;
            margin: 0 4px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .stTabs [role="tab"]:hover {
            background-color: #e0e0e0;
        }
        .stTabs [role="tab"][aria-selected="true"] {
            background-color: #0073e6;
            color: white;
            border-color: #0073e6;
        }
        .chat-box {
            max-height: 500px;
            overflow-y: auto;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 10px;
            background-color: #f9f9f9;
            margin-bottom: 20px;
        }
        .chat-message {
            display: flex;
            align-items: flex-start;
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        .chat-message:last-child {
            border-bottom: none;
        }
        .chat-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .chat-content {
            background-color: #fff;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        .chat-content.user {
            background-color: #0073e6;
            color: #fff;
            align-self: flex-end;
        }
        .chat-content.assistant {
            background-color: #e0e0e0;
            color: #333;
        }
        </style>
        '''
        st.markdown(custom_css, unsafe_allow_html=True)

    # Call the function to inject the CSS
    inject_custom_css()
    MODEL_ROLE = 'ai'
    AI_AVATAR_ICON = '✨'

    # Encode avatars as base64
    user_avatar_base64 = get_base64("./assets/user_avatar.png")
    assistant_avatar_base64 = get_base64("./assets/assitant_avatar.png")

    # Create a data/ folder if it doesn't already exist
    os.makedirs('data/', exist_ok=True)

    # Load past chats (if available)
    try:
        past_chats: dict = joblib.load('data/past_chats_list')
    except:
        past_chats = {}
    
    dummy_response = {
        "status_code": 200,
        "data": {
            "estimated_cost": "$1000",
            "results": [
                "**Day 1:**\n... (Day 1 itinerary)",
                "**Day 2:**\n... (Day 2 itinerary)",
                "**Restaurant Recommendations:**\n... (restaurant details)",
                "**London Hotels: Budget-Friendly, Highly-Rated & Centrally Located:**\n... (hotel details)"
            ]
        }
    }

    def display_chat_popup(message):
        st.subheader(message)

    def parse_response(response_text):
        if isinstance(response_text, list):
            return extract_itinerary_days_from_list(response_text), "", ""
        
        response_text = response_text.strip()
        itinerary_pattern = r"((?:Day\s+\d+|\bDay\s*\d+).*?:.*?)(?=Day\s+\d+|$)"
        restaurant_pattern = r"Restaurant Recommendations:(.*?)(?=Hotel Recommendations:|$)"
        hotel_pattern = r"Hotel Recommendations:(.*)"

        itinerary_matches = re.findall(itinerary_pattern, response_text, re.DOTALL)
        restaurant_matches = re.search(restaurant_pattern, response_text, re.DOTALL)
        hotel_matches = re.search(hotel_pattern, response_text, re.DOTALL)

        itinerary_days = {}
        for match in itinerary_matches:
            lines = match.split("\n", 1)
            day_title = lines[0].strip()
            day_content = lines[1].strip() if len(lines) > 1 else ""
            # Translate the response text
            day_content = translate_text(translate_client, day_content, selected_language_code)

            itinerary_days[day_title] = day_content

        restaurants = restaurant_matches.group(1).strip() if restaurant_matches else ""
        hotels = hotel_matches.group(1).strip() if hotel_matches else ""

        return itinerary_days, restaurants, hotels

    def extract_itinerary_days_from_list(itinerary_list):
        text = itinerary_list[0]
        pattern = r"(Day \d+:.*?)(?=(Day \d+:|$))"
        matches = re.findall(pattern, text, re.DOTALL)
        days = {}
        for match in matches:
            lines = match.split("\n", 1)
            day_title = lines[0].strip()
            day_content = lines[1].strip() if len(lines) > 1 else ""
            days[day_title] = day_content
        return days

    # Initialize Session State Variables
    if "show_results" not in st.session_state:
        st.session_state.show_results = False
    if "show_chat_popup" not in st.session_state:
        st.session_state.show_chat_popup = False

    # --- UI Elements and Logic ---
    st.title("Adventure with :blue[DDExplorer]")

    # Input and button
    with st.container():
        col1, col2 = st.columns([3, 2]) # Adjust column widths as needed
        with col1:
            
            language_options = {
                "English": "en",
                "Hindi": "hi",
                "Spanish": "es",
                "French": "fr",
                "German": "de",
                # Add more languages with their ISO codes here
            }

            selected_language_name = st.selectbox(
                "Select Language:",
                options=list(language_options.keys()),
                index=0,  # Default to English
            )

            # Get the ISO code for the selected language
            selected_language_code = language_options[selected_language_name]

            st.markdown('<div class="stApp search-input"> ', unsafe_allow_html=True)
            place_name = st.text_input("", key="place_input", placeholder="e.g., London, Paris, New York")
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("Explore"):
                if place_name:
                    with st.spinner('Fetching information...'):  # Add spinner
                        response = requests.get(f"{BACKEND_URL}/ai-service", params={"place": place_name})
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data.get("results"), list) and len(data["results"]) > 0:
                            response_text = data["results"][0]
                            itinerary, restaurants, hotels = parse_response(response_text)
                            st.session_state.data = {
                                "estimated_cost": data.get("estimated_cost", "Unknown"),  
                                "itinerary_days": itinerary,
                                "restaurants": restaurants,
                                "hotels": hotels,
                            }
                            st.session_state.show_results = True
                            time.sleep(1)  
                            st.session_state.show_chat_popup = True
                        else:
                            st.error("Invalid response format. 'results' not found or empty.")
                    else:
                        st.error("Failed to fetch data from the backend.")
                else:
                    st.warning("Please enter a place name.")
            

        if st.session_state.show_results:
            with st.container():
                st.markdown("# Travel Guide for {}".format(place_name))
                itinerary_days = st.session_state.data["itinerary_days"]
                day_tabs = list(itinerary_days.keys())
                tabs = st.tabs(["**Itinerary**", "**Restaurant Recommendations**", "**Hotel Recommendations**"])

                with tabs[0]:
                    itinerary_subtabs = st.tabs(day_tabs)
                    for i, day_title in enumerate(day_tabs):
                        with itinerary_subtabs[i]:
                            st.markdown(itinerary_days[day_title])

                with tabs[1]:
                    st.markdown(st.session_state.data["restaurants"], unsafe_allow_html=True)
                
                with tabs[2]:
                    st.markdown(st.session_state.data["hotels"], unsafe_allow_html=True)

    # Function to translate roles between Gemini-Pro and Streamlit terminology
    def translate_role_for_streamlit(user_role):
        return "assistant" if user_role == "model" else user_role

    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])

    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "gemini_history" not in st.session_state:
        st.session_state["gemini_history"] = []

    
    if st.session_state.show_chat_popup:
        # Display chat messages from history
        st.markdown('<div class="chat-box">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            message_role = translate_role_for_streamlit(message['role'])
            message_class = "user" if message_role == "user" else "assistant"
            avatar_base64 = user_avatar_base64 if message_role == "user" else assistant_avatar_base64
            st.markdown(f'''
                <div class="chat-message">
                    <img class="chat-avatar" src="data:image/png;base64,{avatar_base64}" />
                    <div class="chat-content {message_class}">
                        {message['content']}
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if prompt := st.chat_input(f'Would you like help finding flights or hotels for your trip to {place_name}?'):
            st.session_state.messages.append(
                dict(role='user', content=prompt)
            )

            travel_prompt = f"""
                <system-prompt>You are a helpful and informative travel assistant specializing in trips to {place_name}.
                Please answer questions directly related to traveling to {place_name}.
                For example:
                - What are some must-see attractions in {place_name}?
                - What are top Restaurants in {place_name}?
                - Can you suggest some hotels in {place_name}?
                - What is the best time to visit {place_name}?
                - What are some local transportation options in {place_name}?
                - Can you recommend some family-friendly activities in {place_name}?
                If the question is not related to travel to {place_name}, simply state: "I don't have information about that. Please ask me anything related to travel to {place_name}."
                Do not offer any additional hints or suggestions if the question is not travel-related.
                </system-prompt>
                Previous conversation:
                {st.session_state.chat_session.history}

                User's latest question: {prompt}
            """

            response = st.session_state.chat_session.send_message(travel_prompt, stream=True)

            stream_response = ""
            for chunk in response:
                stream_response += chunk.text

            st.session_state.messages.append(
                dict(role=MODEL_ROLE, content=stream_response, avatar=AI_AVATAR_ICON)
            )

            # Display the most recent user message
            st.markdown(f'''
                <div class="chat-message">
                    <img class="chat-avatar" src="data:image/png;base64,{user_avatar_base64}" />
                    <div class="chat-content user">
                        {prompt}
                    </div>
                </div>
            ''', unsafe_allow_html=True)

            # Display the most recent assistant response
            st.markdown(f'''
                <div class="chat-message">
                    <img class="chat-avatar" src="data:image/png;base64,{assistant_avatar_base64}" />
                    <div class="chat-content assistant">
                        {stream_response}
                    </div>
                </div>
            ''', unsafe_allow_html=True)

if __name__ == "__main__":
    show_home()
