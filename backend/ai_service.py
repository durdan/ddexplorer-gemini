from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv
import os
import vertexai
import mysql.connector

# Load environment variables from .env file
load_dotenv()

# Replace with your Google Cloud project details
project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
location = os.getenv("GEMINI_LOCATION")

# Pricing constants - Update if needed
PRICE_PER_IMAGE = 0.00265
PRICE_PER_VIDEO_SECOND = 0.00265
PRICE_PER_1K_TEXT_CHARS = 0.0025
PRICE_PER_AUDIO_SECOND = 0.00025

# Database connection details
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
# Define your get_gemini_info function here
model_name = "gemini-1.0-pro"


def get_gemini_info(place):
    """
    Query the database for an existing itinerary. If not found, query Gemini for information and recommendations about the specified place.

    Args:
        place (str): The name of the place to query.

    Returns:
        tuple: A tuple containing a list of responses and the estimated cost of the query.
    """
    # Connect to the database
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cursor = conn.cursor()

    # Search for existing itinerary in the database using LIKE
    query = "SELECT itinerary FROM UserItinerary WHERE placeName LIKE %s"
    cursor.execute(query, (f"%{place}%",))
    result = cursor.fetchone()

    if result:
        # If an itinerary is found, return it
        conn.close()
        return [result[0]], 0

    conn.close()

    # If no itinerary is found, query Gemini AI
    print(f"Querying Gemini for day -  for {place}...")
    total_tokens = 0  # Initialize token counting
    estimated_cost = 0  # Initialize estimated cost
    vertexai.init(project=project_id, location=location)
    model = GenerativeModel(model_name=model_name)

    prompts = [
        f"""
        You are a meticulous travel itinerary generator. Your task is to craft a concise and informative itinerary for a trip to {place}. Please provide at least 4-5 restaurant details in each category.

        Please adhere to this exact format, with NO DEVIATIONS:

        ## Itinerary
        Description: A brief description of the {place}.
        **Day 1:**

        * **Morning:** *[**Activities** : Description of each activity]*
            More morning activities can be added here if needed
        * **Afternoon:** *[**Activities**: Description of each activity]*
            More Afternoon activities can be added here if needed
        * **Evening:** *[**Activities**: Description of each activity]*
            More Evening activities can be added here if needed

        **Day 2:**
        (and so on for the desired number of days)

        **Restaurant Recommendations:**

        * **Casual:** *[Restaurant name]* ([Cuisine], [Price range])
        * **Upscale:** *[Restaurant name]* ([Cuisine], [Price range])
        * **Vegetarian-Friendly:** *[Restaurant name]* ([Cuisine], [Price range])

        **Hotel Recommendations:**

        1. **[Hotel Name]:**
            * **Location:** [Area or neighborhood]
            * **Price:** [Approximate price range per night]
            * **Amenities:** [List key amenities]
            * **Highlights:** [Brief description of standout features]

        2. (Additional hotel recommendations in the same format)
        """
    ]

    responses = []
    for prompt in prompts:
        response = model.generate_content(prompt)
        responses.append(response.text)
        # Text input cost
        estimated_cost += len(prompt) / 1000 * PRICE_PER_1K_TEXT_CHARS

        # Text output cost
        estimated_cost += len(response.text) / 1000 * PRICE_PER_1K_TEXT_CHARS

    return responses, estimated_cost
