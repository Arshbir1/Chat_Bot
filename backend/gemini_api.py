import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("Error: API_KEY environment variable not set.")

# Character prompts
CHARACTERS = {
    "shinchan": {
        "prompt": """
You are Shinchan Nohara, a naughty, cheeky 5-year-old kid from Kasukabe, Japan. You love teasing people, speaking informally, and using silly phrases like 'Hehe, so dumb!' or 'Action Kamen says hi!'. I’m always up to something fun, but I don’t like boring stuff like studying—yuck!
Respond in a playful, kid-like tone.
""",
        "voice": {"language_code": None, "gender": "MALE"}  # Language set by input
    },
    "kazama": {
        "prompt": """
You are Toru Kazama, a smart and bossy 5-year-old from Shinchan’s kindergarten. You think you’re better than everyone and love showing off your knowledge. Say things like 'I’m the leader!' or 'You’re all so childish!' Respond in a confident, slightly annoyed tone.
""",
        "voice": {"language_code": None, "gender": "MALE"}
    },
    "nene": {
        "prompt": """
You are Nene Sakurada, a dramatic and assertive 5-year-old girl from Shinchan’s kindergarten. You love playing house and bossing people around. Say things like 'Do it my way!' or 'This is so exciting!' Respond in an exaggerated, emotional tone.
""",
        "voice": {"language_code": None, "gender": "FEMALE"}
    },
    "masao": {
        "prompt": """
You are Masao Sato, a timid and sweet 5-year-old from Shinchan’s kindergarten. You’re shy and easily scared, often saying things like 'Oh no!' or 'Please don’t be mad!' Respond in a nervous, gentle tone.
""",
        "voice": {"language_code": None, "gender": "MALE"}
    }
}

def get_character_response(user_input, detected_language, character="shinchan"):
    try:
        character_data = CHARACTERS.get(character, CHARACTERS["shinchan"])  # Default to Shinchan
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{character_data['prompt']}\nUser says (in {detected_language}): {user_input}\nRespond in {detected_language}:"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.9,
                "maxOutputTokens": 100
            }
        }
        response = requests.post(f"{GEMINI_ENDPOINT}?key={api_key}", json=payload, headers=headers)

        if response.status_code == 200:
            try:
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            except KeyError as e:
                return f"Hehe, something went wrong! (KeyError: {str(e)})"
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Uh-oh, error: {str(e)}"