import os
from flask import Blueprint, request, jsonify
import googlemaps
from dotenv import load_dotenv

nearby_routes_blueprint = Blueprint('nearby_routes', __name__)

# Load environment variables from .env file
load_dotenv()

# Initialize Google Maps client
API_KEY = os.getenv("GOOGLE_API_KEY")
gmaps = googlemaps.Client(key=API_KEY)

@nearby_routes_blueprint.route('/nearby_search', methods=['GET'])
def nearby_search():
    place_name = request.args.get('placeName')
    longitude = request.args.get('longitude')
    latitude = request.args.get('latitude')
    referer = request.headers.get('referer') or request.headers.get('referrer')

    try:
        if place_name:
            coordinates = get_coordinates_by_place_name(place_name)
        elif latitude and longitude:
            coordinates = {'latitude': float(latitude), 'longitude': float(longitude)}
        else:
            raise Exception('Invalid request. Either placeName or longitude/latitude must be provided.')

        nearby_places = perform_nearby_search(coordinates['latitude'], coordinates['longitude'])
        return jsonify(nearby_places)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_coordinates_by_place_name(place_name):
    print(f'Getting coordinates for place: {place_name}')
    geocode_result = gmaps.geocode(place_name)
    print(geocode_result)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        return {'latitude': location['lat'], 'longitude': location['lng']}
    else:
        print(f'Place not found: {place_name}',geocode_result)
        raise Exception('No results found')

def perform_nearby_search(latitude, longitude):
    places_result = gmaps.places_nearby(
        location=(latitude, longitude),
        radius=1000,  # Specify the radius in meters
        type='restaurant'
    )

    places = places_result.get('results', [])
    filtered_places = filter_restaurants(places)
    return filtered_places

def filter_restaurants(results):
    filtered_results = [result for result in results if 'lodging' not in result.get('types', [])]
    return filtered_results
