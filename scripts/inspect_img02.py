import os, dotenv
from google import genai
from PIL import Image

dotenv.load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
img = Image.open('dataset/media/images/image_02.png')

resp = client.models.generate_content(
    model='gemini-3.6-flash',
    contents=[img, 'Transcribe all text on this image verbatim. Point out what the exact amount is and what currency and date.']
)
print(resp.text)
