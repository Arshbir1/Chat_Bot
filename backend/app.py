from flask import Flask, render_template, request, jsonify
import os
import time
import atexit
import signal
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage
from record_audio import record_audio
from transcribe_audio import transcribe_audio
from tts import text_to_speech, translate_text
from gemini_api import get_character_response

app = Flask(__name__)

load_dotenv()

firebase_credentials_path = os.getenv('FIREBASE_CREDENTIALS')
if not firebase_credentials_path or not os.path.exists(firebase_credentials_path):
    raise ValueError("FIREBASE_CREDENTIALS not set or file not found in .env file")

firebase_storage_bucket = os.getenv('FIREBASE_STORAGE_BUCKET')
if not firebase_storage_bucket:
    raise ValueError("FIREBASE_STORAGE_BUCKET not set in .env file")

cred = credentials.Certificate(firebase_credentials_path)
firebase_admin.initialize_app(cred, {'storageBucket': firebase_storage_bucket})
db = firestore.client()
bucket = storage.bucket()

UPLOAD_FOLDER = "static/audio"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def clear_firestore():
    print("Clearing Firestore 'conversations' collection...")
    docs = db.collection('conversations').stream()
    for doc in docs:
        doc.reference.delete()

def clear_storage():
    print("Clearing Firebase Storage 'audio/' folder...")
    blobs = bucket.list_blobs(prefix="audio/")
    for blob in blobs:
        blob.delete()

def cleanup():
    print("Cleaning up Firebase data...")
    clear_firestore()
    clear_storage()

atexit.register(cleanup)

def handle_shutdown(signal, frame):
    print("Received SIGINT (Ctrl+C). Performing cleanup...")
    cleanup()
    exit(0)

signal.signal(signal.SIGINT, handle_shutdown)

@app.route('/')
def index():
    cleanup()
    conversation_ref = db.collection('conversations').order_by('timestamp')
    conversation = [doc.to_dict() for doc in conversation_ref.stream()]
    return render_template('index.html', conversation=conversation)

@app.route('/process_audio', methods=['POST'])
def process_audio():
    recorded_audio_path = None
    synthesized_audio_path = None
    try:
        data = request.get_json()
        character = data.get('character', 'shinchan')
        selected_language = data.get('language', 'en-US')
        
        if not selected_language:
            return jsonify({"error": "No language selected"}), 400

        timestamp = str(time.time_ns())
        user_input_id = f"user_input_{timestamp}"
        recorded_audio_path = f"{UPLOAD_FOLDER}/recorded_audio_{timestamp}.wav"
        
        print("Recording audio with voice detection...")
        recording_successful = record_audio(
            recorded_audio_path, 
            max_duration=15,
            silence_threshold=500,
            silence_duration=2.0
        )
        
        if not recording_successful:
            return jsonify({"error": "No speech detected or recording failed"}), 400
        
        recorded_blob_path = f"audio/recorded_audio_{timestamp}.wav"
        recorded_blob = bucket.blob(recorded_blob_path)
        recorded_blob.upload_from_filename(recorded_audio_path)
        recorded_blob.make_public()
        recorded_audio_url = recorded_blob.public_url

        print(f"Transcribing audio in {selected_language}...")
        transcript = transcribe_audio(
            recorded_audio_path,
            language=selected_language
        )
        
        if not transcript:
            return jsonify({"error": "Transcription failed or no speech detected"}), 500

        print(f"Transcription successful: '{transcript}'")

        target_language = selected_language.split("-")[0]
        print(f"Translating transcript from {target_language} to English...")
        transcript_en = translate_text(transcript, "en")

        print(f"Getting {character}'s response in English...")
        response_en = get_character_response(transcript_en, "en-US", character)
        if "Error" in response_en:
            return jsonify({"error": f"Failed to get response: {response_en}"}), 500

        print(f"Translating response to {target_language}...")
        response = translate_text(response_en, target_language)

        synthesized_audio_path = f"{UPLOAD_FOLDER}/synthesized_audio_{timestamp}.mp3"
        text_to_speech(response, selected_language, character, synthesized_audio_path)

        synthesized_blob_path = f"audio/synthesized_audio_{timestamp}.mp3"
        synthesized_blob = bucket.blob(synthesized_blob_path)
        synthesized_blob.upload_from_filename(synthesized_audio_path)
        synthesized_blob.make_public()
        synthesized_audio_url = synthesized_blob.public_url

        conversation_ref = db.collection('conversations')
        conversation_ref.add({
            'user_input_id': user_input_id,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'user_input': transcript,
            'response': response,
            'character': character,
            'selected_language': selected_language,
            'recorded_audio_url': recorded_audio_url,
            'synthesized_audio_url': synthesized_audio_url
        })

        conversation = [doc.to_dict() for doc in conversation_ref.order_by('timestamp').stream()]
        
        return jsonify({
            "transcript": transcript,
            "response": response,
            "character": character,
            "selected_language": selected_language,
            "recorded_audio_url": recorded_audio_url,
            "synthesized_audio_url": synthesized_audio_url,
            "conversation": conversation
        })
    except Exception as e:
        import traceback
        print(f"Error in process_audio: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up local files even on error
        if recorded_audio_path and os.path.exists(recorded_audio_path):
            os.remove(recorded_audio_path)
        if synthesized_audio_path and os.path.exists(synthesized_audio_path):
            os.remove(synthesized_audio_path)

@app.route('/process_text', methods=['POST'])
def process_text():
    synthesized_audio_path = None
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        character = data.get('character', 'shinchan')
        selected_language = data.get('language', 'en-US')
        
        if not selected_language:
            return jsonify({"error": "No language selected"}), 400
        if not text:
            return jsonify({"error": "No text provided"}), 400

        full_language_code = selected_language
        target_language = selected_language.split("-")[0]

        print(f"Translating input text from {target_language} to English...")
        text_en = translate_text(text, "en")

        print(f"Getting {character}'s response in English...")
        response_en = get_character_response(text_en, "en-US", character)
        if "Error" in response_en:
            return jsonify({"error": f"Failed to get response: {response_en}"}), 500

        print(f"Translating response to {target_language}...")
        response = translate_text(response_en, target_language)

        timestamp = str(time.time_ns())
        user_input_id = f"user_input_{timestamp}"
        synthesized_audio_path = f"{UPLOAD_FOLDER}/synthesized_audio_{timestamp}.mp3"
        text_to_speech(response, full_language_code, character, synthesized_audio_path)

        synthesized_blob_path = f"audio/synthesized_audio_{timestamp}.mp3"
        synthesized_blob = bucket.blob(synthesized_blob_path)
        synthesized_blob.upload_from_filename(synthesized_audio_path)
        synthesized_blob.make_public()
        synthesized_audio_url = synthesized_blob.public_url

        conversation_ref = db.collection('conversations')
        conversation_ref.add({
            'user_input_id': user_input_id,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'user_input': text,
            'response': response,
            'character': character,
            'selected_language': full_language_code,
            'recorded_audio_url': None,
            'synthesized_audio_url': synthesized_audio_url
        })

        conversation = [doc.to_dict() for doc in conversation_ref.order_by('timestamp').stream()]
        
        return jsonify({
            "transcript": text,
            "response": response,
            "character": character,
            "selected_language": full_language_code,
            "recorded_audio_url": None,
            "synthesized_audio_url": synthesized_audio_url,
            "conversation": conversation
        })
    except Exception as e:
        import traceback
        print(f"Error in process_text: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up local file even on error
        if synthesized_audio_path and os.path.exists(synthesized_audio_path):
            os.remove(synthesized_audio_path)

if __name__ == '__main__':
    app.run(debug=True, port=5003)