# from dotenv import load_dotenv
# import os
# from gtts import gTTS
# from google.cloud import translate_v3 as translate
# import torchaudio
# import torch
# import numpy as np
# import random
# import re

# load_dotenv()

# translate_client = translate.TranslationServiceClient()

# def translate_text(text, target_language):
#     try:
#         parent = f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global"
#         response = translate_client.translate_text(
#             request={
#                 "parent": parent,
#                 "contents": [text],
#                 "target_language_code": target_language,
#                 "mime_type": "text/plain"
#             }
#         )
#         translated_text = response.translations[0].translated_text
#         print(f"Translated text: {translated_text}")
#         return translated_text
#     except Exception as e:
#         print(f"Translation failed: {str(e)}")
#         return text

# def analyze_text_for_professional_tone(text):
#     sentences = re.split(r'(?<=[.!?])\s+', text.strip())
#     modified_text = []
#     for sentence in sentences:
#         sentence = re.sub(r'\b(hehe|umm|uh|er|like,)\b', '', sentence, flags=re.IGNORECASE)
#         if "!" in sentence:
#             sentence = sentence.replace("!!", "!").replace("!!!", "!")
#             sentence = f"{sentence} "
#         elif "?" in sentence:
#             sentence = f"{sentence} "
#         elif "..." in sentence:
#             sentence = sentence.replace("...", ".")
#         if random.random() < 0.03:
#             professional_phrases = ["Additionally, ", "To clarify, ", "I can confirm that "]
#             if not any(phrase in sentence for phrase in professional_phrases):
#                 if random.random() < 0.5:
#                     sentence = f"{random.choice(professional_phrases)}{sentence}"
#         modified_text.append(sentence)
#     result = " ".join(modified_text)
#     result = result.replace(" so dumb", "")
#     return result

# def add_professional_breathing(waveform, sample_rate):
#     duration = 0.1
#     intensity = 0.005
#     samples = int(duration * sample_rate)
#     breath_pattern = torch.pow(torch.linspace(0, 1, samples), 2)
#     breath = torch.randn(1, samples) * intensity * breath_pattern
#     return torch.cat([breath, waveform], dim=1)

# def apply_professional_voice_variations(waveform, sample_rate, character):
#     waveform = waveform / (torch.max(torch.abs(waveform)) + 1e-6)
    
#     # Character-specific pitch and speed settings
#     voice_settings = {
#         "shinchan": {"pitch_shift": 0.0, "speed_factor": 0.8},  # Increased pitch and speed
#         "kazama": {"pitch_shift": 0.0, "speed_factor": 0.8},    # Neutral pitch, moderate speed
#         "nene": {"pitch_shift": 0.0, "speed_factor": 0.8},      # Higher pitch, faster speed
#         "masao": {"pitch_shift": 0.0, "speed_factor": 0.8}     # Lower pitch, moderate speed
#     }
#     settings = voice_settings.get(character, voice_settings["shinchan"])
    
#     # ---- Adjust Pitch Here ----
#     # pitch_shift: Number of semitones to shift (positive = higher, negative = lower)
#     # Example: 2.0 = 2 semitones up, -1.0 = 1 semitone down
#     if settings["pitch_shift"] != 0.0:
#         waveform = torchaudio.functional.pitch_shift(waveform, sample_rate, settings["pitch_shift"])

#     # ---- Adjust Speed Here ----
#     # speed_factor: > 1.0 speeds up, < 1.0 slows down
#     # Example: 1.5 = 50% faster, 0.8 = 20% slower
#     if settings["speed_factor"] != 1.0:
#         new_sample_rate = int(sample_rate * settings["speed_factor"])
#         waveform = torchaudio.transforms.Resample(sample_rate, new_sample_rate)(waveform)
#         # No padding or truncation to preserve full audio
    
#     # Simplified compression (removed envelope/gain for clarity and speed)
#     waveform = waveform / (torch.max(torch.abs(waveform)) + 1e-6)
#     waveform = waveform * 0.95
    
#     return torch.clamp(waveform, -1.0, 1.0)

# def text_to_speech(text, language_code, character="shinchan", output_file="output.mp3"):
#     # Use the selected language directly for TTS
#     base_language_code = language_code.split("-")[0]  # e.g., "hi" from "hi-IN"
    
#     professional_text = analyze_text_for_professional_tone(text)
#     print(f"Professional text for TTS: {professional_text}")

#     try:
#         print(f"Using Google TTS with language: {base_language_code}")
#         tts = gTTS(text=professional_text, lang=base_language_code, slow=False)
#         temp_file = "temp_output.mp3"
#         tts.save(temp_file)

#         waveform, sample_rate = torchaudio.load(temp_file)
#         waveform = add_professional_breathing(waveform, sample_rate)
#         waveform = apply_professional_voice_variations(waveform, sample_rate, character)
#         torchaudio.save(output_file, waveform, sample_rate, format="mp3")
#         os.remove(temp_file)
#         print(f"Professional TTS audio saved to {output_file} for character: {character} in language: {language_code}")
#     except ValueError as e:
#         print(f"Google TTS error: {str(e)}. Language {base_language_code} not supported.")
#         raise ValueError(f"Cannot generate speech for {language_code}")
#     except Exception as e:
#         print(f"Unexpected Google TTS error: {str(e)}")
#         raise ValueError(f"Failed to generate speech for {language_code}")

# if __name__ == "__main__":
#     # Test in Hindi
#     test_text_hi = "हाय, मैं शिनचन से बात करना चाहता हूँ!"  # "Hi, I want to talk to Shinchan!"
#     print("\nTesting Hindi input:")
#     language_code_hi = "hi-IN"
#     text_to_speech(test_text_hi, language_code_hi, "shinchan", "test_output_hi.mp3")
    
#     # Test in Punjabi
#     test_text_pj = "ਹਾਇ, ਮੈਂ ਸ਼ਿਨਚਨ ਨਾਲ ਗੱਲ ਕਰਨਾ ਚਾਹੁੰਦਾ ਹਾਂ!"  # "Hi, I want to talk to Shinchan!"
#     print("\nTesting Punjabi input:")
#     language_code_pj = "pa-IN"
#     text_to_speech(test_text_pj, language_code_pj, "shinchan", "test_output_pj.mp3")
    
#     # Test with different character
#     print("\nTesting Hindi with Kazama:")
#     text_to_speech(test_text_hi, language_code_hi, "kazama", "test_output_kazama.mp3")
    
#     # Cleanup test files
#     # for file in ["test_output_hi.mp3", "test_output_pj.mp3", "test_output_kazama.mp3"]:
#     #     if os.path.exists(file):
#     #         os.remove(file)
#     #         print(f"Cleaned up {file}")

















# from dotenv import load_dotenv
# import os
# from google.cloud import texttospeech  # Import Google Cloud TTS
# from google.cloud import translate_v3 as translate
# import torchaudio
# import torch
# import numpy as np
# import random
# import re

# load_dotenv()

# # Initialize Google Cloud TTS client
# client = texttospeech.TextToSpeechClient()

# translate_client = translate.TranslationServiceClient()

# def translate_text(text, target_language):
#     try:
#         parent = f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global"
#         response = translate_client.translate_text(
#             request={
#                 "parent": parent,
#                 "contents": [text],
#                 "target_language_code": target_language,
#                 "mime_type": "text/plain"
#             }
#         )
#         translated_text = response.translations[0].translated_text
#         print(f"Translated text: {translated_text}")
#         return translated_text
#     except Exception as e:
#         print(f"Translation failed: {str(e)}")
#         return text

# def analyze_text_for_professional_tone(text):
#     sentences = re.split(r'(?<=[.!?])\s+', text.strip())
#     modified_text = []
#     for sentence in sentences:
#         sentence = re.sub(r'\b(hehe|umm|uh|er|like,)\b', '', sentence, flags=re.IGNORECASE)
#         if "!" in sentence:
#             sentence = sentence.replace("!!", "!").replace("!!!", "!")
#             sentence = f"{sentence} "
#         elif "?" in sentence:
#             sentence = f"{sentence} "
#         elif "..." in sentence:
#             sentence = sentence.replace("...", ".")
#         if random.random() < 0.03:
#             professional_phrases = ["Additionally, ", "To clarify, ", "I can confirm that "]
#             if not any(phrase in sentence for phrase in professional_phrases):
#                 if random.random() < 0.5:
#                     sentence = f"{random.choice(professional_phrases)}{sentence}"
#         modified_text.append(sentence)
#     result = " ".join(modified_text)
#     result = result.replace(" so dumb", "")
#     return result

# def add_professional_breathing(waveform, sample_rate):
#     # duration = 0.1
#     # intensity = 0.005
#     duration = 0.0001
#     intensity = 0.05
#     samples = int(duration * sample_rate)
#     breath_pattern = torch.pow(torch.linspace(0, 1, samples), 2)
#     breath = torch.randn(1, samples) * intensity * breath_pattern
#     return torch.cat([breath, waveform], dim=1)

# def apply_professional_voice_variations(waveform, sample_rate, character):
#     waveform = waveform / (torch.max(torch.abs(waveform)) + 1e-6)
    
#     # Character-specific pitch and speed settings
#     voice_settings = {
#         "shinchan": {"pitch_shift": 0.0, "speed_factor": 0.8},  # Increased pitch and speed
#         "kazama": {"pitch_shift": 0.0, "speed_factor": 0.8},    # Neutral pitch, moderate speed
#         "nene": {"pitch_shift": 0.0, "speed_factor": 0.8},      # Higher pitch, faster speed
#         "masao": {"pitch_shift": 0.0, "speed_factor": 0.8}      # Lower pitch, moderate speed
#     }
#     settings = voice_settings.get(character, voice_settings["shinchan"])
    
#     # ---- Adjust Pitch Here ----
#     # pitch_shift: Number of semitones to shift (positive = higher, negative = lower)
#     # Example: 2.0 = 2 semitones up, -1.0 = 1 semitone down
#     if settings["pitch_shift"] != 0.0:
#         waveform = torchaudio.functional.pitch_shift(waveform, sample_rate, settings["pitch_shift"])

#     # ---- Adjust Speed Here ----
#     # speed_factor: > 1.0 speeds up, < 1.0 slows down
#     # Example: 1.5 = 50% faster, 0.8 = 20% slower
#     if settings["speed_factor"] != 1.0:
#         new_sample_rate = int(sample_rate * settings["speed_factor"])
#         waveform = torchaudio.transforms.Resample(sample_rate, new_sample_rate)(waveform)
#         # No padding or truncation to preserve full audio
    
#     # Simplified compression (removed envelope/gain for clarity and speed)
#     waveform = waveform / (torch.max(torch.abs(waveform)) + 1e-6)
#     waveform = waveform * 0.95
    
#     return torch.clamp(waveform, -1.0, 1.0)

# def text_to_speech(text, language_code, character="shinchan", output_file="output.mp3"):
#     # Use the selected language directly for TTS
#     base_language_code = language_code.split("-")[0]  # e.g., "hi" from "hi-IN"
    
#     # Define voice settings for each character with correct voice names
#     voice_settings = {
#         "shinchan": {
#             "name": "hi-IN-Wavenet-B" if base_language_code == "hi" else 
#                     "pa-IN-Wavenet-B" if base_language_code == "pa" else 
#                     "en-US-Wavenet-D", 
#             "gender": texttospeech.SsmlVoiceGender.MALE
#         },
#         "kazama": {
#             "name": "hi-IN-Wavenet-C" if base_language_code == "hi" else 
#                     "pa-IN-Wavenet-A" if base_language_code == "pa" else 
#                     "en-US-Wavenet-B", 
#             "gender": texttospeech.SsmlVoiceGender.MALE
#         },
#         "nene": {
#             "name": "hi-IN-Wavenet-A" if base_language_code == "hi" else 
#                     "pa-IN-Wavenet-A" if base_language_code == "pa" else 
#                     "en-US-Wavenet-A", 
#             "gender": texttospeech.SsmlVoiceGender.FEMALE
#         },
#         "masao": {
#             "name": "hi-IN-Wavenet-B" if base_language_code == "hi" else 
#                     "pa-IN-Wavenet-A" if base_language_code == "pa" else 
#                     "en-US-Wavenet-C", 
#             "gender": texttospeech.SsmlVoiceGender.MALE
#         }
#     }
#     voice_params = voice_settings.get(character, voice_settings["shinchan"])

#     professional_text = analyze_text_for_professional_tone(text)
#     print(f"Professional text for TTS: {professional_text}")

#     try:
#         # Configure Google Cloud TTS
#         synthesis_input = texttospeech.SynthesisInput(text=professional_text)
#         voice = texttospeech.VoiceSelectionParams(
#             language_code=base_language_code,
#             name=voice_params["name"],
#             ssml_gender=voice_params["gender"]
#         )
#         audio_config = texttospeech.AudioConfig(
#             audio_encoding=texttospeech.AudioEncoding.MP3,
#             speaking_rate=0.8  # Default speed, adjustable if needed
#         )

#         print(f"Using Google Cloud TTS with language: {base_language_code}, voice: {voice_params['name']}")
#         response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

#         # Save initial audio to temporary file
#         temp_file = "temp_output.mp3"
#         with open(temp_file, "wb") as out:
#             out.write(response.audio_content)

#         # Load and process audio
#         waveform, sample_rate = torchaudio.load(temp_file)
#         waveform = add_professional_breathing(waveform, sample_rate)
#         waveform = apply_professional_voice_variations(waveform, sample_rate, character)
#         torchaudio.save(output_file, waveform, sample_rate, format="mp3")
#         os.remove(temp_file)
#         print(f"Professional TTS audio saved to {output_file} for character: {character} in language: {language_code}")
#     except Exception as e:
#         print(f"Google Cloud TTS error: {str(e)}")
#         raise ValueError(f"Failed to generate speech for {language_code}")

# if __name__ == "__main__":
#     # Test in Hindi
#     test_text_hi = "हाय, मैं शिनचन से बात करना चाहता हूँ!"  # "Hi, I want to talk to Shinchan!"
#     print("\nTesting Hindi input:")
#     language_code_hi = "hi-IN"
#     text_to_speech(test_text_hi, language_code_hi, "shinchan", "test_output_hi.mp3")
    
#     # Test in Punjabi
#     test_text_pj = "ਹਾਇ, ਮੈਂ ਸ਼ਿਨਚਨ ਨਾਲ ਗੱਲ ਕਰਨਾ ਚਾਹੁੰਦਾ ਹਾਂ!"  # "Hi, I want to talk to Shinchan!"
#     print("\nTesting Punjabi input:")
#     language_code_pj = "pa-IN"
#     text_to_speech(test_text_pj, language_code_pj, "shinchan", "test_output_pj.mp3")
    
#     # Test with different character
#     print("\nTesting Hindi with Kazama:")
#     text_to_speech(test_text_hi, language_code_hi, "kazama", "test_output_kazama.mp3")
    
#     # Cleanup test files
#     # for file in ["test_output_hi.mp3", "test_output_pj.mp3", "test_output_kazama.mp3"]:
#     #     if os.path.exists(file):
#     #         os.remove(file)
#     #         print(f"Cleaned up {file}")




















from dotenv import load_dotenv
import os
from google.cloud import texttospeech
from google.cloud import translate_v3 as translate
import torchaudio
import torch
import numpy as np
import random
import re

load_dotenv()

# Initialize Google Cloud TTS client
client = texttospeech.TextToSpeechClient()

translate_client = translate.TranslationServiceClient()

def translate_text(text, target_language):
    try:
        parent = f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global"
        response = translate_client.translate_text(
            request={
                "parent": parent,
                "contents": [text],
                "target_language_code": target_language,
                "mime_type": "text/plain"
            }
        )
        translated_text = response.translations[0].translated_text
        print(f"Translated text: {translated_text}")
        return translated_text
    except Exception as e:
        print(f"Translation failed: {str(e)}")
        return text

# def analyze_text_for_professional_tone(text):
#     sentences = re.split(r'(?<=[.!?])\s+', text.strip())
#     modified_text = []
#     for sentence in sentences:
#         sentence = re.sub(r'\b(hehe|umm|uh|er|like,)\b', '', sentence, flags=re.IGNORECASE)
#         if "!" in sentence:
#             sentence = sentence.replace("!!", "!").replace("!!!", "!")
#             sentence = f"{sentence} "
#         elif "?" in sentence:
#             sentence = f"{sentence} "
#         elif "..." in sentence:
#             sentence = sentence.replace("...", ".")
#         if random.random() < 0.03:
#             professional_phrases = ["Additionally, ", "To clarify, ", "I can confirm that "]
#             if not any(phrase in sentence for phrase in professional_phrases):
#                 if random.random() < 0.5:
#                     sentence = f"{random.choice(professional_phrases)}{sentence}"
#         modified_text.append(sentence)
#     result = " ".join(modified_text)
#     result = result.replace(" so dumb", "")
#     return result

def analyze_text_for_professional_tone(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    modified_text = []
    for sentence in sentences:
        sentence = re.sub(r'\b(hehe|umm|uh|er|like,)\b', '', sentence, flags=re.IGNORECASE)
        if "!" in sentence:
            sentence = sentence.replace("!!", "!").replace("!!!", "!")
            sentence = f"{sentence} "
        elif "?" in sentence:
            sentence = f"{sentence} "
        elif "..." in sentence:
            sentence = sentence.replace("...", ".")
        modified_text.append(sentence)
    result = " ".join(modified_text)
    return result

def add_professional_breathing(waveform, sample_rate):
    duration = 0.0001
    intensity = 0.05
    samples = int(duration * sample_rate)
    breath_pattern = torch.pow(torch.linspace(0, 1, samples), 2)
    breath = torch.randn(1, samples) * intensity * breath_pattern
    return torch.cat([breath, waveform], dim=1)

def apply_professional_voice_variations(waveform, sample_rate, character):
    waveform = waveform / (torch.max(torch.abs(waveform)) + 1e-6)
    
    # Character-specific pitch and speed settings
    voice_settings = {
        "shinchan": {"pitch_shift": 0.0, "speed_factor": 0.8},
        "kazama": {"pitch_shift": 0.0, "speed_factor": 0.8},
        "nene": {"pitch_shift": 0.0, "speed_factor": 0.8},
        "masao": {"pitch_shift": 0.0, "speed_factor": 0.8}
    }
    settings = voice_settings.get(character, voice_settings["shinchan"])
    
    # ---- Adjust Pitch Here ----
    # pitch_shift: Number of semitones to shift (positive = higher, negative = lower)
    # Example: 2.0 = 2 semitones up, -1.0 = 1 semitone down
    if settings["pitch_shift"] != 0.0:
        waveform = torchaudio.functional.pitch_shift(waveform, sample_rate, settings["pitch_shift"])

    # ---- Adjust Speed Here ----
    # speed_factor: > 1.0 speeds up, < 1.0 slows down
    # Example: 1.5 = 50% faster, 0.8 = 20% slower
    if settings["speed_factor"] != 1.0:
        new_sample_rate = int(sample_rate * settings["speed_factor"])
        waveform = torchaudio.transforms.Resample(sample_rate, new_sample_rate)(waveform)
        # No padding or truncation to preserve full audio
    
    # Simplified compression (removed envelope/gain for clarity and speed)
    waveform = waveform / (torch.max(torch.abs(waveform)) + 1e-6)
    waveform = waveform * 0.95
    
    return torch.clamp(waveform, -1.0, 1.0)

def text_to_speech(text, language_code, character="shinchan", output_file="output.mp3"):
    base_language_code = language_code.split("-")[0]  # e.g., "hi" from "hi-IN"
    
    # Define voice settings for each character with correct voice names
    voice_settings = {
        "shinchan": {
            "name": (
                "hi-IN-Wavenet-B" if base_language_code == "hi" else
                "ta-IN-Wavenet-B" if base_language_code == "ta" else
                "kn-IN-Wavenet-B" if base_language_code == "kn" else
                "te-IN-Standard-B" if base_language_code == "te" else
                "ml-IN-Wavenet-B" if base_language_code == "ml" else
                "bn-IN-Wavenet-B" if base_language_code == "bn" else
                "mr-IN-Wavenet-B" if base_language_code == "mr" else
                "gu-IN-Wavenet-B" if base_language_code == "gu" else
                "pa-IN-Wavenet-A" if base_language_code == "pa" else  # Only female available
                "ur-IN-Wavenet-A" if base_language_code == "ur" else  # Limited support
                "ja-JP-Wavenet-B" if base_language_code == "ja" else
                "fr-FR-Wavenet-B" if base_language_code == "fr" else
                "de-DE-Wavenet-B" if base_language_code == "de" else
                "es-ES-Wavenet-B" if base_language_code == "es" else
                "en-US-Wavenet-D"  # Fallback
            ),
            "gender": texttospeech.SsmlVoiceGender.MALE
        },
        "kazama": {
            "name": (
                "hi-IN-Wavenet-C" if base_language_code == "hi" else
                "ta-IN-Wavenet-B" if base_language_code == "ta" else
                "kn-IN-Wavenet-B" if base_language_code == "kn" else
                "te-IN-Wavenet-B" if base_language_code == "te" else
                "ml-IN-Wavenet-B" if base_language_code == "ml" else
                "bn-IN-Wavenet-B" if base_language_code == "bn" else
                "mr-IN-Wavenet-B" if base_language_code == "mr" else
                "gu-IN-Wavenet-B" if base_language_code == "gu" else
                "pa-IN-Wavenet-A" if base_language_code == "pa" else
                "ur-IN-Wavenet-A" if base_language_code == "ur" else
                "ja-JP-Wavenet-D" if base_language_code == "ja" else
                "fr-FR-Wavenet-D" if base_language_code == "fr" else
                "de-DE-Wavenet-D" if base_language_code == "de" else
                "es-ES-Wavenet-D" if base_language_code == "es" else
                "en-US-Wavenet-B"
            ),
            "gender": texttospeech.SsmlVoiceGender.MALE
        },
        "nene": {
            "name": (
                "hi-IN-Wavenet-A" if base_language_code == "hi" else
                "ta-IN-Wavenet-A" if base_language_code == "ta" else
                "kn-IN-Wavenet-A" if base_language_code == "kn" else
                "te-IN-Wavenet-A" if base_language_code == "te" else
                "ml-IN-Wavenet-A" if base_language_code == "ml" else
                "bn-IN-Wavenet-A" if base_language_code == "bn" else
                "mr-IN-Wavenet-A" if base_language_code == "mr" else
                "gu-IN-Wavenet-A" if base_language_code == "gu" else
                "pa-IN-Wavenet-A" if base_language_code == "pa" else
                "ur-IN-Wavenet-A" if base_language_code == "ur" else
                "ja-JP-Wavenet-A" if base_language_code == "ja" else
                "fr-FR-Wavenet-A" if base_language_code == "fr" else
                "de-DE-Wavenet-A" if base_language_code == "de" else
                "es-ES-Wavenet-C" if base_language_code == "es" else
                "en-US-Wavenet-A"
            ),
            "gender": texttospeech.SsmlVoiceGender.FEMALE
        },
        "masao": {
            "name": (
                "hi-IN-Wavenet-B" if base_language_code == "hi" else
                "ta-IN-Wavenet-B" if base_language_code == "ta" else
                "kn-IN-Wavenet-B" if base_language_code == "kn" else
                "te-IN-Wavenet-B" if base_language_code == "te" else
                "ml-IN-Wavenet-B" if base_language_code == "ml" else
                "bn-IN-Wavenet-B" if base_language_code == "bn" else
                "mr-IN-Wavenet-B" if base_language_code == "mr" else
                "gu-IN-Wavenet-B" if base_language_code == "gu" else
                "pa-IN-Wavenet-A" if base_language_code == "pa" else
                "ur-IN-Wavenet-A" if base_language_code == "ur" else
                "ja-JP-Wavenet-B" if base_language_code == "ja" else
                "fr-FR-Wavenet-B" if base_language_code == "fr" else
                "de-DE-Wavenet-B" if base_language_code == "de" else
                "es-ES-Wavenet-B" if base_language_code == "es" else
                "en-US-Wavenet-C"
            ),
            "gender": texttospeech.SsmlVoiceGender.MALE
        }
    }
    voice_params = voice_settings.get(character, voice_settings["shinchan"])

    professional_text = analyze_text_for_professional_tone(text)
    print(f"Professional text for TTS: {professional_text}")

    try:
        synthesis_input = texttospeech.SynthesisInput(text=professional_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=base_language_code,
            name=voice_params["name"],
            ssml_gender=voice_params["gender"]
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.8  # Default speed, adjustable if needed
        )

        print(f"Using Google Cloud TTS with language: {base_language_code}, voice: {voice_params['name']}")
        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        temp_file = "temp_output.mp3"
        with open(temp_file, "wb") as out:
            out.write(response.audio_content)

        waveform, sample_rate = torchaudio.load(temp_file)
        waveform = add_professional_breathing(waveform, sample_rate)
        waveform = apply_professional_voice_variations(waveform, sample_rate, character)
        torchaudio.save(output_file, waveform, sample_rate, format="mp3")
        os.remove(temp_file)
        print(f"Professional TTS audio saved to {output_file} for character: {character} in language: {language_code}")
    except Exception as e:
        print(f"Google Cloud TTS error: {str(e)}")
        raise ValueError(f"Failed to generate speech for {language_code}")

if __name__ == "__main__":
    # Base English message to translate
    base_message = "Hi, I want to talk to Shinchan!"

    # Test Shinchan in all supported languages
    tests = [
        ("en-US", base_message),  # English
        ("hi-IN", "हाय, मैं शिनचन से बात करना चाहता हूँ!"),
        ("ta-IN", "வணக்கம், நான் ஷின்சானுடன் பேச விரும்புகிறேன்!"),
        ("kn-IN", "ಹಾಯ್, ನಾನು ಶಿನ್‌ಚಾನ್‌ನೊಂದಿಗೆ ಮಾತನಾಡಲು ಬಯಸುತ್ತೇನೆ!"),
        ("te-IN", "హాయ్, నేను షిన్‌చాన్‌తో మాట్లాడాలనుకుంటున్నాను!"),
        ("ml-IN", "ഹായ്, ഞാൻ ഷിൻചാനുമായി സംസാരിക്കാൻ ആഗ്രഹിക്കുന്നു!"),
        ("bn-IN", "হাই, আমি শিনচানের সঙ্গে কথা বলতে চাই!"),
        ("mr-IN", "हाय, मला शिनचानशी बोलायचं आहे!"),
        ("gu-IN", "હાય, હું શિનચાન સાથે વાત કરવા માંગું છું!"),
        ("pa-IN", "ਹਾਇ, ਮੈਂ ਸ਼ਿਨਚਨ ਨਾਲ ਗੱਲ ਕਰਨਾ ਚਾਹੁੰਦਾ ਹਾਂ!"),
        ("ur-IN", "ہائے، میں شینچان سے بات کرنا چاہتا ہوں!"),
        ("ja-JP", "こんにちは、しんちゃんとお話ししたいです！"),
        ("fr-FR", "Salut, je veux parler à Shinchan !"),
        ("de-DE", "Hallo, ich möchte mit Shinchan sprechen!"),
        ("es-ES", "¡Hola, quiero hablar con Shinchan!")
    ]

    output_files = []
    for lang_code, test_text in tests:
        output_file = f"test_output_shinchan_{lang_code}.mp3"
        print(f"\nTesting Shinchan in {lang_code}:")
        text_to_speech(test_text, lang_code, "shinchan", output_file)
        output_files.append(output_file)

    # Cleanup test files
    # for file in output_files:
    #     if os.path.exists(file):
    #         os.remove(file)
    #         print(f"Cleaned up {file}")