# Character Chatbot

A Flask-based interactive chatbot application that lets users engage in conversations with AI-powered characters through text or voice inputs.

## Features
- **Multi-Character Chat**: Chat with four distinct AI personas—Victor, Jax, Elias, and Lila.
- **Voice & Text Input**: Communicate via speech or text, with real-time transcription and TTS response.
- **Language Support**: Multilingual support with translation capabilities.
- **Cloud Integration**: Uses Firebase for storage and Google Cloud for speech recognition & synthesis.
- **Web-Based Interface**: Interactive UI with a modern chat interface.

## Setup

### 1. Prerequisites
- Python 3.8+
- Flask
- Firebase account with Firestore & Storage configured
- Google Cloud API access for Speech-to-Text and Text-to-Speech
- OpenAI API Key (if using OpenAI models)

### 2. Installation
Clone the repository:
```bash
git clone https://github.com/your-username/character-chatbot.git  
cd character-chatbot  
```
Install dependencies:
```bash
pip install -r requirements.txt  
```

### 3. Environment Variables
Create a `.env` file and add the required API keys:
```
API_KEY=your_gemini_api_key  
FIREBASE_CREDENTIALS=path/to/your/firebase-credentials.json  
FIREBASE_STORAGE_BUCKET=your-firebase-bucket-name  
GOOGLE_CLOUD_PROJECT=your-google-cloud-project  
```

### 4. Run the Application
```bash
python app.py  
```
Open your browser and go to `http://127.0.0.1:5000/`.

## File Structure
```
/character-chatbot  
│── static/  
│   ├── style.css         # Frontend styles  
│   ├── script.js         # Chat UI interactions  
│── templates/  
│   ├── index.html        # Main page  
│   ├── character_template.html # Chat interface  
│── app.py                # Flask backend  
│── gemini_api.py         # AI response generation  
│── record_audio.py       # Audio recording logic  
│── transcribe_audio.py   # Speech-to-text using Google Cloud  
│── tts.py                # Text-to-speech processing  
│── requirements.txt      # Dependencies  
│── README.md             # Project documentation  
```

## API Endpoints
- **`/`** - Home page  
- **`/<character>`** - Chat page for a specific character  
- **`/process_audio`** - Handles voice input  
- **`/process_text`** - Handles text input  

## Credits
Developed by [Your Name].

## License
MIT License.
