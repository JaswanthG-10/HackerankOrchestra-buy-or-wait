import pandas as pd

events = pd.read_csv('dataset/financial_events.csv').set_index('event_id', drop=False)
linked = events[events['linked_event_id'].notna()]

print(f"Total linked events: {len(linked)}")
for ev_id, row in linked.iterrows():
    parent_id = row['linked_event_id']
    if parent_id in events.index:
        p = events.loc[parent_id]
        p_info = f"{p['event_id']}:{p['status']}:{p['direction']}:{p['amount']}:{p['description']}"
    else:
        p_info = "MISSING_PARENT"
    c_info = f"{row['event_id']}:{row['status']}:{row['direction']}:{row['amount']}:{row['description']}"
    print(f"[{row['user_id']}] {p_info}  --->  {c_info}")
