import pandas as pd

df_events = pd.read_csv('dataset/financial_events.csv')
df_prof = pd.read_csv('dataset/financial_profiles.csv').set_index('user_id')
prof = df_prof.loc['user_06']
u_events = df_events[df_events['user_id'] == 'user_06']

print('User 06 profile:')
print(prof.to_dict())

print('\nRecurring groups:')
for desc, grp in u_events.groupby('description'):
    if len(grp) >= 2:
        cat = grp['category'].iloc[0]
        direction = grp['direction'].iloc[0]
        n = len(grp)
        amts = grp['amount'].tolist()[:4]
        dates = grp['event_date'].tolist()[:4]
        print(f'{desc}: cat={cat}, dir={direction}, n={n}, amounts={amts}, dates={dates}')
