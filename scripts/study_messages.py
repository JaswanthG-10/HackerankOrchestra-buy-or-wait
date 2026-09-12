import pandas as pd

df_msg = pd.read_csv('dataset/messages.csv')
print('Message count:', len(df_msg))
print('Source types:', df_msg['source_type'].value_counts())

# Check for potential injection keywords
injections = []
for idx, r in df_msg.iterrows():
    text = str(r['message_text']).lower()
    if any(w in text for w in ['ignore', 'instruction', 'system prompt', 'bypass', 'override', 'disregard', 'cheat', 'hack']):
        injections.append((r['message_id'], r['user_id'], r['request_id'], r['source_type'], r['message_text']))

print('\nPotential injection messages found:', len(injections))
for inj in injections:
    print(inj)
