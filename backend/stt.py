# from google.cloud import speech_v1p1beta1 as speech

# def transcribe_audio(audio_file):
#     client = speech.SpeechClient()
#     with open(audio_file, "rb") as f:
#         content = f.read()
#     audio = speech.RecognitionAudio(content=content)
#     config = {
#     "encoding": speech.RecognitionConfig.AudioEncoding.LINEAR16,
#     "sample_rate_hertz": 16000,
#     "language_code": "hi-IN"  # Corrected!
# }
#     response = client.recognize(config=config, audio=audio)
#     for result in response.results:
#         return result.alternatives[0].transcript, result.language_code
#     return None, None
from google.cloud import speech

def transcribe_audio(audio_file):
    client = speech.SpeechClient()

    with open(audio_file, "rb") as f:
        audio_content = f.read()

    audio = speech.RecognitionAudio(content=audio_content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",  # Default language
        alternative_language_codes=["hi-IN", "es-ES", "fr-FR", "de-DE"],  # Other languages to detect
        enable_automatic_punctuation=True,
    )

    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        transcript = result.alternatives[0].transcript
        confidence = result.alternatives[0].confidence
        detected_language = result.language_code  # This gets the detected language

        print(f"🎤 Transcription: {transcript}")
        print(f"✅ Confidence: {confidence}")
        print(f"🌍 Detected Language: {detected_language}")

        return transcript, detected_language  # Now returning two values

    return None, None  # Return None if no valid response
