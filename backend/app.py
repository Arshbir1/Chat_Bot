from flask import Flask, render_template, request, jsonify
import os
import time
import atexit  # For shutdown hook
import signal  # For handling Ctrl+C
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage
from record_audio import record_audio
from transcribe_audio import transcribe_audio
from tts import text_to_speech
from gemini_api import get_character_response

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Load Firebase credentials from .env
firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS')
print(f"Firebase credentials path: {firebase_credentials_path}")
print(f"File exists: {os.path.exists(firebase_credentials_path)}")
if not firebase_credentials_path:
    raise ValueError("FIREBASE_CREDENTIALS not set in .env file")

firebase_storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')
print(f"Firebase storage bucket: {firebase_storage_bucket}")
if not firebase_storage_bucket:
    raise ValueError("FIREBASE_STORAGE_BUCKET not set in .env file")

# Initialize Firebase
cred = credentials.Certificate(firebase_credentials_path)
firebase_admin.initialize_app(cred, {
    'storageBucket': firebase_storage_bucket
})
db = firestore.client()
bucket = storage.bucket()

# Paths for temporary audio files
UPLOAD_FOLDER = "static/audio"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Helper function to clear all documents in the 'conversations' collection
def clear_firestore():
    try:
        print("Clearing Firestore 'conversations' collection...")
        conversation_ref = db.collection('conversations')
        docs = conversation_ref.stream()
        deleted_count = 0
        for doc in docs:
            doc.reference.delete()
            deleted_count += 1
        print(f"Firestore 'conversations' collection cleared. Deleted {deleted_count} documents.")
    except Exception as e:
        print(f"Error clearing Firestore: {str(e)}")

# Helper function to clear all files in the 'audio/' folder in Firebase Storage
def clear_storage():
    try:
        print("Clearing Firebase Storage 'audio/' folder...")
        blobs = bucket.list_blobs(prefix="audio/")
        deleted_count = 0
        for blob in blobs:
            blob.delete()
            deleted_count += 1
        print(f"Firebase Storage 'audio/' folder cleared. Deleted {deleted_count} files.")
    except Exception as e:
        print(f"Error clearing Firebase Storage: {str(e)}")

# Cleanup function to run on shutdown or when loading the website
def cleanup():
    print("Cleaning up Firebase data...")
    clear_firestore()
    clear_storage()
    print("Cleanup completed.")

# Register the cleanup function to run on exit
atexit.register(cleanup)

# Handle Ctrl+C (SIGINT) gracefully
def handle_shutdown(signal, frame):
    print("Received SIGINT (Ctrl+C). Performing cleanup...")
    cleanup()
    exit(0)

signal.signal(signal.SIGINT, handle_shutdown)

@app.route('/')
def index():
    # Clear Firestore and Storage when the website is loaded
    cleanup()

    # Retrieve conversation history from Firestore (should be empty after cleanup)
    conversation_ref = db.collection('conversations').order_by('timestamp')
    conversation_docs = conversation_ref.stream()
    conversation = [doc.to_dict() for doc in conversation_docs]
    print(f"Loaded {len(conversation)} conversations from Firestore.")
    return render_template('index.html', conversation=conversation)

@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        # Get the selected character from the request
        data = request.get_json()
        character = data.get('character', 'shinchan')

        # Step 1: Record audio with a unique filename
        print("Starting audio recording...")
        timestamp = str(time.time_ns())  # Nanosecond precision for uniqueness
        user_input_id = f"user_input_{timestamp}"  # Unique ID for this QnA pair
        recorded_audio_path = f"{UPLOAD_FOLDER}/recorded_audio_{timestamp}.wav"
        print(f"Recording audio to: {recorded_audio_path}")
        record_audio(recorded_audio_path, duration=5)

        # Step 2: Upload recorded audio to Firebase Storage
        recorded_blob_path = f"audio/recorded_audio_{timestamp}.wav"
        print(f"Uploading recorded audio to Firebase Storage: {recorded_blob_path}")
        recorded_blob = bucket.blob(recorded_blob_path)
        recorded_blob.upload_from_filename(recorded_audio_path)
        recorded_blob.make_public()
        recorded_audio_url = recorded_blob.public_url
        print(f"Recorded audio URL: {recorded_audio_url}")

        # Step 3: Transcribe the recorded audio
        print("Transcribing audio...")
        transcript, detected_language = transcribe_audio(recorded_audio_path)
        if transcript is None:
            return jsonify({"error": "Transcription failed. No speech detected or STT API error."}), 500

        # Step 4: Get character's response
        print(f"Getting {character}'s response for transcript: {transcript} (Language: {detected_language})")
        response = get_character_response(transcript, detected_language, character)
        if "Error" in response or "broke something" in response:
            return jsonify({"error": f"Failed to get {character}'s response: {response}"}), 500

        # Step 5: Synthesize response with ElevenLabs TTS
        print(f"Synthesizing {character}'s response to speech...")
        synthesized_audio_path = f"{UPLOAD_FOLDER}/synthesized_audio_{timestamp}.mp3"  # ElevenLabs uses MP3
        print(f"Synthesizing audio to: {synthesized_audio_path}")
        text_to_speech(response, detected_language, character, synthesized_audio_path)

        # Step 6: Upload synthesized audio to Firebase Storage
        synthesized_blob_path = f"audio/synthesized_audio_{timestamp}.mp3"
        print(f"Uploading synthesized audio to Firebase Storage: {synthesized_blob_path}")
        synthesized_blob = bucket.blob(synthesized_blob_path)
        synthesized_blob.upload_from_filename(synthesized_audio_path)
        synthesized_blob.make_public()
        synthesized_audio_url = synthesized_blob.public_url
        print(f"Synthesized audio URL: {synthesized_audio_url}")

        # Step 7: Store QnA data in Firestore
        conversation_ref = db.collection('conversations')
        conversation_ref.add({
            'user_input_id': user_input_id,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'user_input': transcript,
            'response': response,
            'character': character,
            'detected_language': detected_language,
            'recorded_audio_url': recorded_audio_url,
            'synthesized_audio_url': synthesized_audio_url
        })

        # Step 8: Retrieve updated conversation history
        conversation_docs = conversation_ref.order_by('timestamp').stream()
        conversation = [doc.to_dict() for doc in conversation_docs]

        # Clean up local files
        os.remove(recorded_audio_path)
        os.remove(synthesized_audio_path)

        return jsonify({
            "transcript": transcript,
            "response": response,
            "character": character,
            "detected_language": detected_language,
            "recorded_audio_url": recorded_audio_url,
            "synthesized_audio_url": synthesized_audio_url,
            "conversation": conversation
        })
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/process_text', methods=['POST'])
def process_text():
    try:
        # Get text and character from the request
        data = request.get_json()
        text = data.get('text', '').strip()
        character = data.get('character', 'shinchan')
        if not text:
            return jsonify({"error": "No text provided."}), 400

        # Assume detected_language as 'en' for text input
        detected_language = 'en'

        # Step 1: Get character's response
        print(f"Getting {character}'s response for text: {text} (Language: {detected_language})")
        response = get_character_response(text, detected_language, character)
        if "Error" in response or "broke something" in response:
            return jsonify({"error": f"Failed to get {character}'s response: {response}"}), 500

        # Step 2: Synthesize response with ElevenLabs TTS
        print(f"Synthesizing {character}'s response to speech...")
        timestamp = str(time.time_ns())  # Nanosecond precision for uniqueness
        user_input_id = f"user_input_{timestamp}"  # Unique ID for this QnA pair
        synthesized_audio_path = f"{UPLOAD_FOLDER}/synthesized_audio_{timestamp}.mp3"  # ElevenLabs uses MP3
        print(f"Synthesizing audio to: {synthesized_audio_path}")
        text_to_speech(response, detected_language, character, synthesized_audio_path)

        # Step 3: Upload synthesized audio to Firebase Storage
        synthesized_blob_path = f"audio/synthesized_audio_{timestamp}.mp3"
        print(f"Uploading synthesized audio to Firebase Storage: {synthesized_blob_path}")
        synthesized_blob = bucket.blob(synthesized_blob_path)
        synthesized_blob.upload_from_filename(synthesized_audio_path)
        synthesized_blob.make_public()
        synthesized_audio_url = synthesized_blob.public_url
        print(f"Synthesized audio URL: {synthesized_audio_url}")

        # Step 4: Store QnA data in Firestore
        conversation_ref = db.collection('conversations')
        conversation_ref.add({
            'user_input_id': user_input_id,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'user_input': text,
            'response': response,
            'character': character,
            'detected_language': detected_language,
            'recorded_audio_url': None,  # No recorded audio for text input
            'synthesized_audio_url': synthesized_audio_url
        })

        # Step 5: Retrieve updated conversation history
        conversation_docs = conversation_ref.order_by('timestamp').stream()
        conversation = [doc.to_dict() for doc in conversation_docs]

        # Clean up local file
        os.remove(synthesized_audio_path)

        return jsonify({
            "transcript": text,
            "response": response,
            "character": character,
            "detected_language": detected_language,
            "recorded_audio_url": None,
            "synthesized_audio_url": synthesized_audio_url,
            "conversation": conversation
        })
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003)