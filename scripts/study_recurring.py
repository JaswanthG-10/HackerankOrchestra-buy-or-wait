import pandas as pd

df = pd.read_csv('dataset/financial_events.csv')
for u in ['user_01', 'user_02', 'user_03', 'user_06', 'user_11']:
    u_events = df[df['user_id'] == u]
    print(f'=== {u} ({len(u_events)} events) ===')
    # look at value counts of descriptions
    vc = u_events['description'].value_counts()
    print('Frequent descriptions (>1 times):')
    for desc, count in vc[vc > 1].items():
        sub = u_events[u_events['description'] == desc]
        cat = sub['category'].iloc[0]
        direction = sub['direction'].iloc[0]
        amounts = sub['amount'].tolist()
        flex = sub['flexibility'].iloc[0]
        dates = sub['event_date'].tolist()
        print(f'  {desc} (n={count}, cat={cat}, dir={direction}, flex={flex}): amounts={amounts[:3]} dates={dates[:3]}')
