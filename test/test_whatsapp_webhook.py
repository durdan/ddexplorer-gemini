import unittest
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'http://localhost:5000/webhook')

class TestWhatsAppWebhook(unittest.TestCase):

    def test_webhook_verification(self):
        params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': os.getenv('VERIFY_TOKEN'),
            'hub.challenge': 'test_challenge'
        }
        response = requests.get(WEBHOOK_URL, params=params)
        print(response.text)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, 'test_challenge')

    def test_incoming_text_message(self):
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "1234567890",
                                        "id": "message_id_1",
                                        "text": "Hello"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        response = requests.post(WEBHOOK_URL, json=payload)
        self.assertEqual(response.status_code, 200)

    def test_build_itinerary_flow(self):
        # Simulate sending the "Build Itinerary" interactive message
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "1234567890",
                                        "id": "message_id_2",
                                        "interactive": {
                                            "type": "list_reply",
                                            "list_reply": {
                                                "id": "Build Itinerary"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        response = requests.post(WEBHOOK_URL, json=payload)
        self.assertEqual(response.status_code, 200)

        # Simulate user response with city name
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "1234567890",
                                        "id": "message_id_3",
                                        "text": "Paris"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        response = requests.post(WEBHOOK_URL, json=payload)
        self.assertEqual(response.status_code, 200)

    def test_plan_road_trip_flow(self):
        # Simulate sending the "Plan Road Trip" interactive message
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "1234567890",
                                        "id": "message_id_4",
                                        "interactive": {
                                            "type": "list_reply",
                                            "list_reply": {
                                                "id": "Plan Road Trip"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        response = requests.post(WEBHOOK_URL, json=payload)
        self.assertEqual(response.status_code, 200)

        # Simulate user response with start city name
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "1234567890",
                                        "id": "message_id_5",
                                        "text": "New York"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        response = requests.post(WEBHOOK_URL, json=payload)
        self.assertEqual(response.status_code, 200)

        # Simulate user response with end city name
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "1234567890",
                                        "id": "message_id_6",
                                        "text": "Los Angeles"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        response = requests.post(WEBHOOK_URL, json=payload)
        self.assertEqual(response.status_code, 200)

    def test_find_restaurant_flow(self):
        # Simulate sending the "Find Restaurant" interactive message
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "1234567890",
                                        "id": "message_id_7",
                                        "interactive": {
                                            "type": "list_reply",
                                            "list_reply": {
                                                "id": "Find Restaurant"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        response = requests.post(WEBHOOK_URL, json=payload)
        self.assertEqual(response.status_code, 200)

        # Simulate user response with place name
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "1234567890",
                                        "id": "message_id_8",
                                        "text": "Central Park"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        response = requests.post(WEBHOOK_URL, json=payload)
        self.assertEqual(response.status_code, 200)

        # Simulate user sending location
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "1234567890",
                                        "id": "message_id_9",
                                        "location": {
                                            "latitude": "40.785091",
                                            "longitude": "-73.968285"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        response = requests.post(WEBHOOK_URL, json=payload)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
