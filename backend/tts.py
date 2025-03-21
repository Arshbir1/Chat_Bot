import os
import json
from google.cloud import texttospeech, translate
from google.oauth2 import service_account
import requests

def text_to_speech(text, language_code, character, output_file):
    """
    Convert text to speech using Google Cloud Text-to-Speech or ElevenLabs
    
    Args:
        text: Text to convert to speech
        language_code: Language code (e.g., "en-US")
        character: Character name (e.g., "shinchan")
        output_file: Path to save the output audio file
    
    Returns:
        True if successful, False otherwise
    """
    # Load credentials from environment variable
    google_credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if not google_credentials_json:
        print("Error: GOOGLE_APPLICATION_CREDENTIALS_JSON not set in environment variables")
        return False

    try:
        credentials_info = json.loads(google_credentials_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
    except Exception as e:
        print(f"Error loading Google Cloud credentials: {str(e)}")
        return False

    # Initialize the Text-to-Speech client with the credentials
    try:
        client = texttospeech.TextToSpeechClient(credentials=credentials)
    except Exception as e:
        print(f"Error initializing TextToSpeechClient: {str(e)}")
        return False

    # Configure the voice based on the character
    voice_name = "en-US-Wavenet-D"  # Default voice
    if character == "shinchan":
        voice_name = "en-US-Wavenet-A"  # Example voice for Shinchan
    elif character == "doraemon":
        voice_name = "en-US-Wavenet-B"  # Example voice for Doraemon

    # Configure the voice parameters
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
    )

    # Configure the audio output
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.1,
        pitch=2.0,
    )

    # Synthesize the speech
    synthesis_input = texttospeech.SynthesisInput(text=text)
    try:
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )
        with open(output_file, "wb") as out:
            out.write(response.audio_content)
        return True
    except Exception as e:
        print(f"Error during text-to-speech synthesis: {str(e)}")
        return False

def translate_text(text, target_language):
    """
    Translate text to the target language using Google Cloud Translate
    
    Args:
        text: Text to translate
        target_language: Target language code (e.g., "en")
    
    Returns:
        Translated text or original text if translation fails
    """
    # Load credentials from environment variable
    google_credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if not google_credentials_json:
        print("Error: GOOGLE_APPLICATION_CREDENTIALS_JSON not set in environment variables")
        return text

    try:
        credentials_info = json.loads(google_credentials_json)
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
    except Exception as e:
        print(f"Error loading Google Cloud credentials: {str(e)}")
        return text

    # Initialize the Translate client with the credentials
    try:
        client = translate.TranslationServiceClient(credentials=credentials)
    except Exception as e:
        print(f"Error initializing TranslationServiceClient: {str(e)}")
        return text

    parent = f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global"
    try:
        response = client.translate_text(
            request={
                "parent": parent,
                "contents": [text],
                "mime_type": "text/plain",
                "source_language_code": None,
                "target_language_code": target_language,
            }
        )
        return response.translations[0].translated_text
    except Exception as e:
        print(f"Error during translation: {str(e)}")
        return text
