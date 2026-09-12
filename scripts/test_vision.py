import os
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
print('API key loaded:', bool(api_key))

client = genai.Client(api_key=api_key)

img_path = 'dataset/media/images/image_01.png'
img = Image.open(img_path)

prompt = '''You are an expert financial document parser. 
Extract the exact total financial amount and currency from this document.
Return a JSON object with:
- amount: float (numeric amount only, no commas or currency symbols)
- currency: string (e.g. IDR, INR, USD, EUR, ZAR)
- description: string (brief description of what this document is)
'''

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[img, prompt],
    config=dict(response_mime_type='application/json')
)

print('Response:')
print(response.text)
