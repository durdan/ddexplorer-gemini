import os
from flask import Flask, Blueprint,request, jsonify
import requests
import logging
from dotenv import load_dotenv
import googlemaps
from user_management import create_user

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app and Google Maps client

API_KEY = os.getenv("GOOGLE_API_KEY")
gmaps = googlemaps.Client(key=API_KEY)
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
API_ENDPOINT = os.getenv('API_ENDPOINT')
TOKEN = os.getenv('TOKEN')
APP_URL = os.getenv('APP_URL')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define blueprints
nearby_routes_blueprint = Blueprint('nearby_routes', __name__)
whatsapp_webhook_blueprint = Blueprint('whatsapp_webhook', __name__)

pending_responses = {}
processed_messages = []

# Helper functions
def send_message(sender_id, message):
    headers = {
        'Content-type': 'application/json',
        'Authorization': f'Bearer {TOKEN}'
    }
    data = {
        'messaging_product': 'whatsapp',
        'to': sender_id,
        **message
    }
    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=data)
        response.raise_for_status()
        logger.info("Message sent successfully!")
    except requests.RequestException as e:
        logger.error(f"Error sending message: {e}")
        raise

def generate_text_message_template(text):
    return {
        'preview_url': True,
        'text': {
            'body': text
        }
    }

def generate_menu_message_template():
    return {
        'type': 'interactive',
        'interactive': {
            'type': 'list',
            'header': {
                'type': 'text',
                'text': '👋DDExplorer - Explore, Plan, and Discover'
            },
            'body': {
                'text': 'Your Ultimate Holiday Companion:'
            },
            'action': {
                'button': 'Menu',
                'sections': [
                    {
                        'title': 'Plan your Travel',
                        'rows': [
                            {
                                'id': 'Build Itinerary',
                                'title': 'Build Itinerary',
                                'description': 'Explore with us'
                            },
                            {
                                'id': 'Plan Road Trip',
                                'title': 'Plan Road Trip',
                                'description': 'Road trip with detailed routes, attractions'
                            },
                            {
                                'id': 'Find Restaurant',
                                'title': 'Find Restaurants',
                                'description': 'Search nearby restaurants'
                            }
                        ]
                    }
                ]
            }
        }
    }

def split_message_into_parts(message, part_size):
    parts = []
    while len(message) > part_size:
        part = message[:part_size]
        parts.append(part)
        message = message[part_size:]
    parts.append(message)
    return parts

def extract_the_list(nearby_places):
    restaurant_details = [f"""
    Name: {item['name']}
    Address: {item['vicinity']}
    Rating: {item.get('rating', 'N/A')}
    Total Reviews: {item.get('user_ratings_total'), 'N/A'}
    Map: https://www.google.com/maps/search/?api=1&query={item['geometry']['location']['lat']},{item['geometry']['location']['lng']}&query_place_id={item['place_id']}
    --------------""" for item in nearby_places]
    return '\n'.join(restaurant_details)

@nearby_routes_blueprint.route('/nearby_search', methods=['GET'])
def nearby_search():
    place_name = request.args.get('placeName')
    longitude = request.args.get('longitude')
    latitude = request.args.get('latitude')

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
    print("Getting coordinates for place:",place_name)
    geocode_result = gmaps.geocode(place_name)
    print("GeoCode....",geocode_result)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        return {'latitude': location['lat'], 'longitude': location['lng']}
    else:
        print( "Errort",geocode_result)
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

@whatsapp_webhook_blueprint.route('', methods=['GET', 'POST'])
def webhook_handler():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403

    if request.method == 'POST':
        data = request.json
        if data['object'] == 'whatsapp_business_account':
            entry = data['entry'][0]
            changes = entry['changes'][0]
            message = changes['value']
            if message.get('messages'):
                received_message = message['messages'][0]
                if received_message.get('from'):
                    handle_incoming_message(received_message)
        return '', 200

def remove_processed_message(message_id):
    if message_id in processed_messages:
        processed_messages.remove(message_id)

def handle_incoming_message(received_message):
    from_id = received_message['from']
    message_id = received_message['id']

    if message_id in processed_messages:
        logger.info("Duplicate message received. Ignoring...")
        return

    processed_messages.append(message_id)
    if len(processed_messages) >= 200:
        processed_messages.clear()
        logger.info("Processed messages array cleared.")

    if 'button' in received_message and received_message['button']['payload'] == 'Build Itinerary':
        send_message(from_id, generate_text_message_template("Please enter *city or country* name"))
        pending_responses[from_id] = {'type': 'itinerary', 'city': ''}
    elif 'interactive' in received_message and received_message['interactive']['type'] == 'list_reply' and received_message['interactive']['list_reply']['id'] == 'Build Itinerary':
        send_message(from_id, generate_text_message_template("Please enter *city or country* name"))
        pending_responses[from_id] = {'type': 'itinerary', 'city': ''}
    elif 'button' in received_message and received_message['button']['payload'] == 'Plan Road Trip':
        send_message(from_id, generate_text_message_template("Please enter *start city* name"))
        pending_responses[from_id] = {'type': 'roadtrip', 'start_city': '', 'end_city': ''}
    elif 'interactive' in received_message and received_message['interactive']['type'] == 'list_reply' and received_message['interactive']['list_reply']['id'] == 'Plan Road Trip':
        send_message(from_id, generate_text_message_template("Please enter *start city* name"))
        pending_responses[from_id] = {'type': 'roadtrip', 'start_city': '', 'end_city': ''}
    elif 'interactive' in received_message and received_message['interactive']['type'] == 'list_reply' and received_message['interactive']['list_reply']['id'] == 'Find Restaurant':
        send_message(from_id, generate_text_message_template("Please send your location or enter the place name."))
        pending_responses[from_id] = {'type': 'restaurant', 'place_name': '', 'location': None}
    else:
        if from_id in pending_responses:
            response = pending_responses[from_id]
            if response['type'] == 'itinerary':
                handle_itinerary_response(from_id, received_message, response)
            elif response['type'] == 'roadtrip':
                handle_roadtrip_response(from_id, received_message, response)
            elif response['type'] == 'restaurant':
                handle_restaurant_response(from_id, received_message, response)
        else:
            create_user(from_id)
            send_message(from_id, generate_menu_message_template())

def handle_itinerary_response(from_id, received_message, response):
    if not response['city']:
        response['city'] = received_message['text']
        send_message(from_id, generate_text_message_template("Thank you for reaching out to us! We have received your request and are working on it. Please sit back and relax, and we'll provide a response to you shortly."))
        # Simulate processing and response
        process_itinerary_request(from_id, response['city'])
        send_message(from_id, generate_menu_message_template())
        del pending_responses[from_id]
        remove_processed_message(received_message['id'])

def handle_roadtrip_response(from_id, received_message, response):
    if not response['start_city']:
        response['start_city'] = received_message['text']
        send_message(from_id, generate_text_message_template("Please enter *end city* name"))
    elif not response['end_city']:
        response['end_city'] = received_message['text']
        send_message(from_id, generate_text_message_template("Thank you for reaching out to us! We have received your request and are working on it. Please sit back and relax, and we'll provide a response to you shortly."))
        # Simulate processing and response
        process_roadtrip_request(from_id, response['start_city'], response['end_city'])
        del pending_responses[from_id]
        remove_processed_message(received_message['id'])

def handle_restaurant_response(from_id, received_message, response):
    if not response['place_name'] and not response['location']:
        if 'text' in received_message:  # Check if text is present in the received_message
            response['place_name'] = received_message['text']
        elif 'location' in received_message:  # Check if location is present in the received_message
            location = received_message['location']
            response['location'] = location
        else:
            return  # No place name or location found, return without further processing

        send_message(from_id, generate_text_message_template("Thank you for reaching out to us! We have received your request and are working on it. Please sit back and relax, and we'll provide a response to you shortly."))

        # Simulate processing and response
        if response['place_name']:
            process_restaurant_request(from_id, place_name=response['place_name'])
        elif response['location']:
            process_restaurant_request(from_id, location=response['location'])
        send_message(from_id, generate_menu_message_template())
        del pending_responses[from_id]
        remove_processed_message(received_message['id'])




def process_restaurant_request(from_id, place_name=None, location=None):
    try:
        if place_name and isinstance(place_name, dict) and 'body' in place_name:
            if isinstance(place_name['body'], dict) and 'body' in place_name['body']:
                place_name = place_name['body']['body']
            else:
                place_name = place_name['body']

        print("Processing restaurant request...", place_name, location)

        if place_name:
            params = {'placeName': place_name}
        elif location:
            params = {'latitude': location['latitude'], 'longitude': location['longitude']}
        else:
            return

        print("Params:", params)  # Debugging statement

        response = requests.get(f"{APP_URL}/nearby_search", params=params)
        response.raise_for_status()
        nearby_places = response.json()
        print("Nearby places:", nearby_places)  # Debugging statement

        places_list = extract_the_list(nearby_places)
        parts = split_message_into_parts(places_list, 4096)

        for part in parts:
            send_message(from_id, generate_text_message_template(part))
    except requests.RequestException as e:
        logger.error(f"Error processing restaurant request: {e}")
        send_message(from_id, generate_text_message_template("Sorry, we couldn't process your request at the moment. Please try again later."))




 

def process_itinerary_request(from_id, city):
    # Simulate a call to /ai-service endpoint
    ai_service_url = f"{APP_URL}/ai-service"
    if city and isinstance(city, dict) and 'body' in city:
            if isinstance(city['body'], dict) and 'body' in city['body']:
                city = city['body']['body']
            else:
                city = city['body']
    params = {"place": city, "phone_number": from_id}
    
    try:
        response = requests.get(ai_service_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data:
            itinerary = data["results"][0]  # Assuming there's only one itinerary result
            print( "Itinerary.....",itinerary)
            parts = split_message_into_parts(itinerary, 4096)

            for part in parts:
                send_message(from_id, generate_text_message_template(part))
        else:
            send_message(from_id, generate_text_message_template("No itinerary found for the specified city."))
    except requests.RequestException as e:
        print( "Itinerary1111111",itinerary)
        logger.error(f"Error processing itinerary request: {e}")
        send_message(from_id, generate_text_message_template("Sorry, we couldn't process your request at the moment. Please try again later."))



def process_roadtrip_request(from_id, start_city, end_city):
    # Add logic to process roadtrip request here
    pass


