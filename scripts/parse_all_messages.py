import os, json, time, dotenv
from google import genai
import pandas as pd

dotenv.load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

df_msg = pd.read_csv('dataset/messages.csv')
cache_file = 'code/cache/messages.json'

cache = {}
if os.path.exists(cache_file):
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache = json.load(f)
    except Exception:
        cache = {}

print(f'Starting with {len(cache)} cached messages', flush=True)

# Replace NaN with None for clean JSON
df_clean = df_msg.where(pd.notnull(df_msg), None)
all_records = df_clean.to_dict(orient='records')
batch_size = 20

total_input_tokens = 0
total_output_tokens = 0

for start_idx in range(0, len(all_records), batch_size):
    batch_num = start_idx // batch_size + 1
    batch = all_records[start_idx:start_idx + batch_size]
    uncached = [m for m in batch if str(m['message_id']) not in cache]
    
    if not uncached:
        print(f'Batch {batch_num} already cached.', flush=True)
        continue

    print(f'Processing Batch {batch_num} ({len(uncached)} messages)...', flush=True)
    prompt = '''You are a financial information extractor for personal cash flow forecasting.
For each message in the provided list, extract key structured facts into a JSON list.
Available fact_types:
- "salary_update": confirmed regular or next salary amount / date change
- "expense_amendment": recurring expense change (e.g. rent increase %, subscription change)
- "internal_transfer": transfer between user's own bank accounts (net zero cash flow)
- "pending_unconfirmed": pending bonus, commission, refund, prize, payout, or invoice that is NOT yet confirmed/settled (do NOT count as cash)
- "unrealized_investment": investment market valuation change without sale (no cash proceeds)
- "other": informational

For each message, return an object with:
- "message_id": string
- "user_id": string
- "related_event_id": string or null
- "fact_type": string (one of the above)
- "new_amount": float or null (extracted numeric amount if explicitly stated)
- "currency": string or null
- "percentage_change": float or null (e.g. 12.0 for a 12% increase)
- "effective_date": string or null (YYYY-MM-DD)
- "is_confirmed_cash": boolean (True ONLY if this is confirmed liquid cash inflow; False for pending bonuses, pending refunds, unrealized investments, internal transfers)
- "summary": string (concise explanation of the financial effect)

Input messages:
''' + json.dumps(uncached, ensure_ascii=False)

    retries = 0
    while retries < 5:
        try:
            resp = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=[prompt],
                config=dict(response_mime_type='application/json')
            )
            parsed = json.loads(resp.text)
            for item in parsed:
                m_id = str(item['message_id'])
                cache[m_id] = item

            usage = resp.usage_metadata
            if usage:
                total_input_tokens += usage.prompt_token_count or 0
                total_output_tokens += usage.candidates_token_count or 0

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2)
            print(f'Batch {batch_num} SUCCESS: cached {len(parsed)} items. Total now: {len(cache)}', flush=True)
            time.sleep(12)
            break
        except Exception as e:
            print(f'Retry {retries + 1} on batch {batch_num}: {e}', flush=True)
            retries += 1
            time.sleep(15)

print(f'All messages processed! Total cached: {len(cache)}', flush=True)
print(f'Total input tokens: {total_input_tokens}, total output tokens: {total_output_tokens}', flush=True)
