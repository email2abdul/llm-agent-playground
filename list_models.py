import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Tumhari API key ke liye kaun-kaun se models available hain — sab print karo
print("Available models jo generateContent support karte hain:\n")

for model in client.models.list():
    # Sirf wo models dikhao jo text generate kar sakte hain
    if "generateContent" in (model.supported_actions or []):
        print(f"  - {model.name}")
