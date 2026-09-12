import os, json, time, dotenv
from google import genai
import pandas as pd

dotenv.load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

df_msg = pd.read_csv('dataset/messages.csv')
batch = df_msg.head(20).to_dict(orient='records')

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
''' + json.dumps(batch, ensure_ascii=False)

resp = client.models.generate_content(
    model='gemini-3.6-flash',
    contents=[prompt],
    config=dict(response_mime_type='application/json')
)

results = json.loads(resp.text)
print(f'Batch 1 parsed {len(results)} messages:')
for r in results[:5]:
    print(r)
