# translation.py

from google.cloud import translate_v2 as translate

def initialize_translation_client(key_path):
    # Initialize the translation client with the service account key
    translate_client = translate.Client.from_service_account_json(key_path)
    return translate_client

def translate_text(translate_client, text, target_language):
    # Translate the text using the translation client
    translation = translate_client.translate(text, target_language=target_language)
    translated_text = translation['translatedText']
    return translated_text
