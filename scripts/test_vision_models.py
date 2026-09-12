import os, dotenv
from google import genai
from PIL import Image

dotenv.load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

img_path = 'dataset/media/images/image_01.png'
img = Image.open(img_path)

prompt = '''You are an expert financial document parser. 
Extract the exact total financial amount and currency from this document.
Return a JSON object with:
- amount: float (numeric amount only, no commas or currency symbols)
- currency: string (e.g. IDR, INR, USD, EUR, ZAR)
- description: string (brief description of what this document is)
'''

for model in ['gemini-2.5-flash-lite', 'gemini-3.6-flash', 'gemini-flash-latest']:
    try:
        response = client.models.generate_content(
            model=model,
            contents=[img, prompt],
            config=dict(response_mime_type='application/json')
        )
        print(f'Model {model} SUCCESS:')
        print(response.text)
        break
    except Exception as e:
        print(f'Model {model} failed: {e}')
