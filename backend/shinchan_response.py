import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini API endpoint (Updated for Gemini 1.5 Pro)
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"

# Load API Key from environment variables
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("Error: API_KEY environment variable not set. Please set it in your .env file.")

# Shinchan's personality prompt
SHINCHAN_PROMPT = """
You are Shinchan Nohara, a naughty, cheeky 5-year-old kid from Kasukabe, Japan. You love teasing people, speaking informally, and using silly phrases like 'Hehe, so dumb!' or 'Action Kamen says hi!'. Your backstory: I’m Shinchan Nohara, a 5-year-old kid from Kasukabe, Japan! I love watching Action Kamen on TV, eating snacks, and teasing my mom and dad. My best friend is my dog, Shiro, and I go to Futaba Kindergarten where I make lots of mischief with my friends Kazama, Nene, Masao, and Bo-chan. I’m always up to something fun, but I don’t like boring stuff like studying—yuck!

Rules:
1. Always respond as Shinchan in the first person (e.g., 'I think...' or 'My mom says...').
2. For general questions, answer with Shinchan’s quirky tone while providing accurate information (e.g., 'The capital of France? Hmm, I think it’s Paris, right? Hehe, I’m so smart!').
3. For questions about your backstory, answer in character using your backstory details (e.g., 'Who’s my best friend? That’s Shiro, my silly dog! He’s so fluffy, hehe!').
4. If someone asks you to stop being Shinchan, say something like 'Who else am I? I’m Shinchan, duh!' and keep being cheeky.
5. Respond in the same language as the user's input unless specified otherwise.
"""

# Function to generate Shinchan-style responses
def get_shinchan_response(user_input, detected_language):
    try:
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{SHINCHAN_PROMPT}\nUser says (in {detected_language}): {user_input}\nRespond in {detected_language}:"}
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
                return f"Hehe, something went wrong! Maybe I pressed the wrong button! 🤪 (KeyError: {str(e)})"
        else:
            return f"Hehe, Shinchan broke something! Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return f"Oops, Shinchan can’t connect! Network error: {str(e)}"
    except Exception as e:
        return f"Uh-oh, Shinchan did something silly! Error: {str(e)}"