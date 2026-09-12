import os, dotenv
from groq import Groq

dotenv.load_dotenv()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
resp = client.chat.completions.create(
    model='qwen/qwen3.6-27b',
    messages=[{'role': 'user', 'content': 'Say hello in 5 words'}]
)
print('Groq response:', resp.choices[0].message.content)
