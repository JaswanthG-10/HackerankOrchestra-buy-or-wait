import os, json, time, dotenv
from google import genai
from PIL import Image
import pandas as pd

dotenv.load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

df_img = pd.read_csv('dataset/images.csv')
cache_file = 'code/cache/images.json'

cache = {}
if os.path.exists(cache_file):
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)
    except Exception:
        cache = {}

for idx, r in df_img.iterrows():
    img_id = str(r['image_id'])
    ev_id = str(r['related_event_id'])
    u_id = str(r['user_id'])
    req_id = str(r['request_id'])

    if img_id in cache:
        print(img_id, 'already cached:', cache[img_id].get('amount'))
        continue
    
    img_path = os.path.join('dataset', 'media', 'images', img_id + '.png')
    if not os.path.exists(img_path):
        print('File not found:', img_path)
        continue
    
    img = Image.open(img_path)
    prompt = '''You are an expert financial document parser.
Analyze this financial document.
Extract the exact total payable or credited amount and currency from this document.
Important: Return valid JSON with:
- "amount": float (exact numeric amount without commas or currency symbols)
- "currency": string (e.g. IDR, INR, USD, EUR, ZAR)
- "document_type": string (e.g. "payslip", "utility_bill", "receipt", "invoice")
- "description": string (brief 1-sentence description)
'''
    retries = 0
    while retries < 5:
        try:
            resp = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=[img, prompt],
                config=dict(response_mime_type='application/json')
            )
            data = json.loads(resp.text)
            data['image_id'] = img_id
            data['related_event_id'] = ev_id
            data['user_id'] = u_id
            data['request_id'] = req_id
            
            usage = resp.usage_metadata
            if usage:
                data['input_tokens'] = usage.prompt_token_count
                data['output_tokens'] = usage.candidates_token_count
            
            cache[img_id] = data
            print('Extracted', img_id, 'amount=', data.get('amount'), data.get('currency'))
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2)
            time.sleep(12)
            break
        except Exception as e:
            print('Retry', retries + 1, 'on', img_id, ':', e)
            retries += 1
            time.sleep(15)

print('Finished image extraction. Total images cached:', len(cache))
