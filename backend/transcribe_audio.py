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

    print(f"STT Configuration: Primary language = {config.language_code}, Alternative languages = {config.alternative_language_codes}")

    response = client.recognize(config=config, audio=audio)

    if not response.results:
        print("No speech detected in the audio.")
        return None, None

    for result in response.results:
        transcript = result.alternatives[0].transcript
        confidence = result.alternatives[0].confidence
        detected_language = result.language_code  # This gets the detected language

        print(f"🎤 Transcription: {transcript}")
        print(f"✅ Confidence: {confidence}")
        print(f"🌍 Detected Language: {detected_language}")

        # Debug: Print all alternatives to see if English was considered
        for i, alt in enumerate(result.alternatives):
            print(f"Alternative {i}: {alt.transcript} (Confidence: {alt.confidence})")

        return transcript, detected_language

    return None, None  # Return None if no valid response