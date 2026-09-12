import pandas as pd

df_msg = pd.read_csv('dataset/messages.csv')
with open('all_messages_dump.txt', 'w', encoding='utf-8') as f:
    for idx, r in df_msg.iterrows():
        f.write(str(r['message_id']) + ' | ' + str(r['user_id']) + ' | req=' + str(r['request_id']) + ' | ev=' + str(r['related_event_id']) + ' | src=' + str(r['source_type']) + '\n')
        f.write('  ' + str(r['message_text']) + '\n\n')

print('Wrote all 215 messages to all_messages_dump.txt')
