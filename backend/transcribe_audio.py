import os
import json
from google.cloud import speech
from google.oauth2 import service_account

def transcribe_audio(audio_file_path, language="en-US"):
    """
    Transcribe audio file using Google Cloud Speech-to-Text
    
    Args:
        audio_file_path: Path to the audio file
        language: Language code (e.g., "en-US")
    
    Returns:
        Transcribed text or None if transcription fails
    """
    # Load credentials from environment variable
    google_credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if not google_credentials_json:
        print("Error: GOOGLE_APPLICATION_CREDENTIALS_JSON not set in environment variables")
        return None

    print(f"Loaded GOOGLE_APPLICATION_CREDENTIALS_JSON: {google_credentials_json[:50]}...")  # Print first 50 chars for debugging

    try:
        credentials_info = json.loads(google_credentials_json)
        print(f"Credentials info loaded: {list(credentials_info.keys())}")
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        print("Credentials object created successfully")
    except Exception as e:
        print(f"Error loading Google Cloud credentials: {str(e)}")
        return None

    # Initialize the Speech client with the credentials
    try:
        speech_client = speech.SpeechClient(credentials=credentials)
        print("SpeechClient initialized successfully")
    except Exception as e:
        print(f"Error initializing SpeechClient: {str(e)}")
        return None

    # Read the audio file
    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code=language,
        enable_automatic_punctuation=True,
    )

    try:
        response = speech_client.recognize(config=config, audio=audio)
        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript
        return transcript.strip()
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return None
