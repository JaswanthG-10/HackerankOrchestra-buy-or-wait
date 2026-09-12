import pandas as pd

df_fx = pd.read_csv('dataset/exchange_rates.csv')
print('FX count:', len(df_fx))
print('Columns:', df_fx.columns.tolist())
print('Pairs:')
print(df_fx.groupby(['from_currency', 'to_currency']).size())
print('\nDate range:', df_fx['rate_date'].min(), 'to', df_fx['rate_date'].max())
print('\nSample rows:')
print(df_fx.head(10))
