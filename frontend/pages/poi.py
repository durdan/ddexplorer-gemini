import googlemaps
import streamlit as st
import os
from dotenv import load_dotenv
 
# Load environment variables from .env file
load_dotenv()
# Google Maps API Key (Replace 'YOUR_API_KEY' with your actual key)

API_KEY = os.getenv("GOOGLE_API_KEY")
gmaps = googlemaps.Client(key=API_KEY)

st.title("Tourist Itinerary Builder")

# User Input
placename = st.text_input("Enter a place (city, address, landmark):")
radius_miles = st.number_input("Radius (miles)", min_value=1, max_value=200, value=50)  
radius_meters = radius_miles * 1609.34  # Convert miles to meters

if st.button("Search"):
    if placename:
        # Geocode place to get coordinates
        geocode_result = gmaps.geocode(placename)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']

            # Search for POIs within the radius
            places_result = gmaps.places_nearby(
                location=location,
                radius=radius_meters,
                type='tourist_attraction'  # You can adjust the type (e.g., 'museum', 'park', 'restaurant')
            )

            st.subheader("Points of Interest:")
            for place in places_result['results']:
                st.write(f"- {place['name']} ({place['types']})")

                # Optionally, display additional details (address, rating, etc.)
                # st.write(place['vicinity'])
                # if 'rating' in place:
                #     st.write(f"  Rating: {place['rating']}")

        else:
            st.error("Place not found.")
    else:
        st.warning("Please enter a place.")
