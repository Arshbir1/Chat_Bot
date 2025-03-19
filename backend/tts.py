from dotenv import load_dotenv
import os
from elevenlabs.client import ElevenLabs

load_dotenv()

# Initialize ElevenLabs client
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Map characters to ElevenLabs voice IDs (replace with actual voice IDs from your ElevenLabs account)
CHARACTER_VOICES = {
    "shinchan": "pNInz6obpgDQGcFmaJgB",  # Example: Adam (male voice)
    "kazama": "MF3mGyEYCl7XYWbV9V6O",   # Example: Bill (male voice)
    "nene": "21m00Tcm4TlvDq8ikWAM",    # Example: Rachel (female voice)
    "masao": "yoZ06aMxZJJ28mfd3POQ"    # Example: Sam (male voice)
}

def text_to_speech(text, language_code, character, output_file):
    """
    Convert text to speech using ElevenLabs API.
    
    Args:
        text (str): The text to convert to speech.
        language_code (str): Language code (e.g., 'en-US', 'hi-IN').
        character (str): The character (shinchan, kazama, nene, masao).
        output_file (str): Path to save the MP3 output.
    """
    # Get the voice ID for the character
    voice_id = CHARACTER_VOICES.get(character, CHARACTER_VOICES["shinchan"])  # Default to Shinchan

    # Generate audio as a generator
    audio_generator = client.generate(
        text=text,
        voice=voice_id,
        model="eleven_multilingual_v2",  # Supports multiple languages
        output_format="mp3_44100_128"    # MP3 format, 44.1kHz, 128kbps
    )

    # Collect audio data from the generator
    audio_bytes = b"".join(audio_generator)

    # Save the audio to the output file
    with open(output_file, "wb") as f:
        f.write(audio_bytes)

# Test the function
if __name__ == "__main__":
    if "ELEVENLABS_API_KEY" not in os.environ:
        print("ELEVENLABS_API_KEY is not set in the environment.")
    else:
        print(f"ELEVENLABS_API_KEY is set.")
        test_text = "Hehe, I’m Shinchan, so dumb!"
        test_language = "en-US"
        test_character = "shinchan"
        test_output = "test_output.mp3"
        text_to_speech(test_text, test_language, test_character, test_output)
        print(f"Generated audio saved to {test_output}")