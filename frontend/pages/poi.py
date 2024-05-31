import streamlit as st
import googlemaps
import os
from dotenv import load_dotenv

def show_poi():
    load_dotenv()
    API_KEY = os.getenv("GOOGLE_API_KEY")
    gmaps = googlemaps.Client(key=API_KEY)

    st.title("Tourist Itinerary Builder")

    placename = st.text_input("Enter a place (city, address, landmark):")
    radius_miles = st.number_input("Radius (miles)", min_value=1, max_value=200, value=50)  
    radius_meters = radius_miles * 1609.34

    if st.button("Search"):
        if placename:
            geocode_result = gmaps.geocode(placename)
            if geocode_result:
                location = geocode_result[0]['geometry']['location']

                # 1. Initial Search (Broader)
                places_result = gmaps.places_nearby(
                    location=location,
                    radius=radius_meters,
                    type=['tourist_attraction']  # Broader type initially
                )

                # 2. Filter by Types (Optional)
                # Uncomment if you want to prioritize certain types
                # filtered_results = [place for place in places_result['results'] if any(t in place['types'] for t in ['historical_landmark'])]
                # places_result['results'] = filtered_results

                # 3. Sort by Combined Ranking
                places_result['results'].sort(
                    key=lambda x: (-x.get('user_ratings_total', 0), 
                                   -x.get('rating', 0),
                                    x.get('distance', float('inf')))  # Closer is better
                )

                st.subheader("Top Points of Interest:")
                for i, place in enumerate(places_result['results'][:10]):
                    st.write(f"{i+1}. {place['name']} ({place['types']})")
                    if 'rating' in place:
                        st.write(f"   Rating: {place['rating']}")
                    if 'user_ratings_total' in place:
                        st.write(f"   User Ratings: {place['user_ratings_total']}")

            else:
                st.error("Place not found.")
        else:
            st.warning("Please enter a place.")
