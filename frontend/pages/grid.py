import streamlit as st
from PIL import Image
import googlemaps
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Display the image
image = Image.open('./assets/bg.webp')
st.image(image, caption='Tourist Attractions in Jaipur, India')

# Initialize Google Maps client
API_KEY = os.getenv("GOOGLE_API_KEY")
gmaps = googlemaps.Client(key=API_KEY)

# Function to fetch attractions from Google Places API
def get_attractions(location):
    max_results=10
    try:
        geocode_result = gmaps.geocode(location)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']

            # Initial Search (Broader)
            places = gmaps.places_nearby(
                location=location,
                radius=10000,
                rank_by='prominence' ,
                keyword="landmark OR tourist attraction OR historical site",
                type='tourist_attraction' # Broader type initially
            )
           # Filter by specific types and photo availability
            filtered_places = [
                place for place in places['results'] 
                if place.get('types') and not any(t in ['travel_agent', 'business'] for t in place['types'])
                and 'photos' in place  # Check for photos key
            ]

            # Limit results if needed after filtering
            filtered_places = filtered_places[:max_results]

            place_ids = [place['place_id'] for place in filtered_places]
            attractions = fetch_place_details(place_ids)

            return attractions
    except googlemaps.exceptions.ApiError as e:
        st.error(f"Error fetching attractions: {e}")

# Helper function to fetch details for a batch of place_ids
def fetch_place_details(place_ids):
    batch_size = 10  # Define your batch size
    place_id_batches = [place_ids[i:i + batch_size] for i in range(0, len(place_ids), batch_size)]

    attractions = []

    for batch in place_id_batches:
        for place_id in batch:
            try:
                place_details = gmaps.place(place_id)
                result = place_details['result']
                
                image_url = ""
                if 'photos' in result:
                    photo_reference = result['photos'][0]['photo_reference']
                    image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={API_KEY}"
                
                # Use editorial_summary if available, otherwise use vicinity
                description = result.get('editorial_summary', {}).get('overview', result.get('vicinity', 'N/A'))
                
                attraction = {
                    'name': result.get('name', 'N/A'),
                    'image_url': image_url,
                    'description': description,
                    'rating': result.get('rating', 'N/A'),
                    'phone_number': result.get('formatted_phone_number', 'N/A'),
                    'website_url': result.get('website', 'N/A')
                }
                attractions.append(attraction)
            except googlemaps.exceptions.ApiError as e:
                st.error(f"Error fetching place details: {e}")
            time.sleep(0.1)  # Add a small delay to avoid hitting rate limits

    return attractions

# Function to display each attraction's details in a card-like format
def display_attraction(attraction):
    rating = attraction['rating']
    if isinstance(rating, (int, float)):
        rating_stars = '★' * int(rating) + '☆' * (5 - int(rating))
    else:
        rating_stars = 'No rating available'

    # Check for individual buttons instead of both at once
    has_phone = attraction['phone_number'] != 'N/A'
    has_website = attraction['website_url'] != 'N/A'

    phone_button_html = f'<a href="tel:{attraction["phone_number"]}" style="padding: 8px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-right: 5px;">📞 Phone</a>' if has_phone else ''
    website_button_html = f'<a href="{attraction["website_url"]}" style="padding: 8px; background-color: #2196F3; color: white; text-decoration: none; border-radius: 5px;">🌐 Website</a>' if has_website else ''

    buttons_html = (
        f'<div style="display: flex; justify-content: space-between; flex-wrap: wrap;">{phone_button_html}{website_button_html}</div>' 
        if has_phone or has_website 
        else ''
    )

    st.markdown(
        f"""
        <div style="border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);">
            <h3>{attraction['name']}</h3>
            <img src="{attraction['image_url']}" style="max-height: 200px; width: 100%; object-fit: cover; border-radius: 5px;" />
            <p>{attraction['description']}</p>
            <p>Rating: {rating_stars}</p>
            {buttons_html} 
        </div>
        """, 
        unsafe_allow_html=True
    )



# ... (rest of the code is the same)

# Get attractions for a specified location
location = st.text_input("Enter location (e.g., Jaipur):")
if location:
    with st.spinner('Fetching attractions...'):
        attractions = get_attractions(location)
        if attractions:
            cols = st.columns(2)
            for i, attraction in enumerate(attractions):
                with cols[i % 2]:
                    display_attraction(attraction)

