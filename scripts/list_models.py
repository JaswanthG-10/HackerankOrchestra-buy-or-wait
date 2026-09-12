import os, dotenv
from google import genai

dotenv.load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
try:
    for m in client.models.list():
        if 'generateContent' in m.supported_actions or True:
            print(m.name)
except Exception as e:
    print('List models error:', e)
