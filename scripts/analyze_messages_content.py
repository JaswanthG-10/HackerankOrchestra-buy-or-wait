import pandas as pd
import re

df_msg = pd.read_csv('dataset/messages.csv')
print('Total messages:', len(df_msg))
print('Users with messages:', df_msg['user_id'].nunique())
print('Requests with messages:', df_msg['request_id'].dropna().nunique())
print('Related events:', df_msg['related_event_id'].dropna().nunique())

# Let's inspect unique message patterns
patterns = {}
for idx, r in df_msg.iterrows():
    txt = r['message_text']
    # replace numbers and dates with placeholders to find template patterns
    norm = re.sub(r'\d{4}-\d{2}-\d{2}', '<DATE>', txt)
    norm = re.sub(r'[A-Z]{3}\s*[\d,]+(\.\d+)?', '<MONEY>', norm)
    norm = re.sub(r'EMP-\d+|SER-\d+|FIN-\d+|BAN-\d+|MER-\d+', '<REF>', norm)
    norm = norm[:60]
    patterns[norm] = patterns.get(norm, 0) + 1

print(f'\nTop normalized patterns ({len(patterns)} distinct):')
for pat, cnt in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:15]:
    print(f'  [{cnt}] {pat}')
