import pandas as pd
msgs = pd.read_csv('dataset/messages.csv')
print(f"Total messages: {len(msgs)}")
for idx, r in msgs.head(25).iterrows():
    print(f"[{r['user_id']}] ({r['source_type']}) {r['message_text']}")
