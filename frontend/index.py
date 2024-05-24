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
# Load environment variables from .env file
load_dotenv()

# Backend API URL
BACKEND_URL = "http://localhost:5000"  # Update with your backend URL

# Replace with your Google Cloud project details
project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
location = os.getenv("GEMINI_LOCATION")

# Define your get_gemini_info function here
model_name = "gemini-1.0-pro"

vertexai.init(project=project_id, location=location)
model = GenerativeModel(model_name=model_name)
def inject_custom_css():
    with open("./css/stylesheet.css") as f:
        css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    
# Call the function to inject the CSS
inject_custom_css()
MODEL_ROLE = 'ai'
AI_AVATAR_ICON = '✨'

# Create a data/ folder if it doesn't already exist
try:
    os.mkdir('data/')
except:
    pass

# Load past chats (if available)
try:
    past_chats: dict = joblib.load('data/past_chats_list')
except:
    past_chats = {}
dummy_response = {
    "status_code": 200,  # HTTP status code
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
    # Check if response_text is a list (from database)
    if isinstance(response_text, list):
        return extract_itinerary_days_from_list(response_text), "", ""
    
    # If response_text is a string (from Gemini API)
    itinerary_pattern = r"(Day \d+:.*?)(?=Day \d+:|$)"
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
        itinerary_days[day_title] = day_content

    restaurants = restaurant_matches.group(1).strip() if restaurant_matches else ""
    hotels = hotel_matches.group(1).strip() if hotel_matches else ""

    return itinerary_days, restaurants, hotels

def extract_itinerary_days_from_list(itinerary_list):
    text = itinerary_list[0]  # Assuming the itinerary is the first element in the list
    pattern = r"(Day \d+:.*?)(?=(Day \d+:|$))"  # Regex to match each day's details
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

st.title("Plan Your Next Adventure with :blue[DDExplorer]")

# Input and button
with st.container():
    col1, col2 = st.columns([3, 2]) 

    with col1:
        # Wrap the text_input in a div with a custom class
        st.markdown('<div class="stApp search-input"> ', unsafe_allow_html=True)
        place_name = st.text_input("", key="place_input", placeholder="e.g., London, Paris, New York")
        st.markdown('</div>', unsafe_allow_html=True)
     
        # Render the button using st.markdown
        if st.button("Explore"):
        
            if place_name:
                response = requests.get(f"{BACKEND_URL}/ai-service", params={"place": place_name})
                if response.status_code == 200:
                    data = response.json()
                    # Check for proper format of 'results' and 'estimated_cost'
                    if isinstance(data.get("results"), list) and len(data["results"]) > 0:
                        response_text = data["results"][0]  # Extract response text 
                        itinerary, restaurants, hotels = parse_response(response_text)
                        st.session_state.data = {
                            "estimated_cost": data.get("estimated_cost", "Unknown"),  
                            "itinerary_days": itinerary,
                            "restaurants": restaurants,
                            "hotels": hotels,
                        }
                        st.session_state.show_results = True
                        # Trigger chat popup after a delay
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

            # Extract days from itinerary
            itinerary_days = st.session_state.data["itinerary_days"]
            day_tabs = list(itinerary_days.keys())
            
            # Create main tabs
            tabs = st.tabs(["Itinerary", "Restaurant Recommendations", "Hotel Recommendations"])
            
            # Itinerary Tab
            with tabs[0]:  # Access the first tab (index 0)
                # Sub-tabs for Itinerary
                itinerary_subtabs = st.tabs(day_tabs)
                for i, day_title in enumerate(day_tabs):
                    with itinerary_subtabs[i]:  # Access each sub-tab by index
                        st.markdown(itinerary_days[day_title])

            # Restaurant Recommendations Tab
            with tabs[1]:  # Access the second tab (index 1)
                st.markdown(st.session_state.data["restaurants"], unsafe_allow_html=True)
            
            # Hotel Recommendations Tab
            with tabs[2]:  # Access the third tab (index 2)
                st.markdown(st.session_state.data["hotels"], unsafe_allow_html=True)

# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role

# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Chat history (allows to ask multiple questions)
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "gemini_history" not in st.session_state:
    st.session_state["gemini_history"] = []

if st.session_state.show_chat_popup:
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(
            name=message['role'],
            avatar=message.get('avatar'),
        ):
            st.markdown(message['content'])

    # React to user input
    if prompt := st.chat_input('Would you like help finding flights or hotels for your trip to...'+place_name):
        # Display user message in chat message container
        with st.chat_message('user'):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append(
            dict(
                role='user',
                content=prompt,
            )
        )
        travel_prompt = f"""
                <system-prompt>You are a helpful and informative travel assistant specializing in trips to {place_name}.
                Please answer questions directly related to traveling to {place_name}.
                For example:
                - What are some must-see attractions in {place_name}?
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
        # Send message to AI
        response = st.session_state.chat_session.send_message(
            travel_prompt,
            stream=True,
        )
        # Display assistant response in chat message container
        with st.chat_message(
            name=MODEL_ROLE,
            avatar=AI_AVATAR_ICON,
        ):
            stream_response = ""
            for chunk in response:
                stream_response += chunk
                st.markdown(stream_response)
            # Add assistant response to chat history
            st.session_state.messages.append(
                dict(
                    role=MODEL_ROLE,
                    content=stream_response,
                    avatar=AI_AVATAR_ICON,
                )
            )









