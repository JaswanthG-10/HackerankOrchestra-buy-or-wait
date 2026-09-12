import pandas as pd
df_msg = pd.read_csv('dataset/messages.csv').set_index('message_id')
unclass_ids = ['message_67', 'message_69', 'message_92', 'message_106', 'message_108', 'message_114', 'message_118', 'message_121', 'message_134', 'message_136', 'message_142', 'message_145', 'message_157', 'message_161', 'message_163', 'message_164', 'message_179', 'message_183', 'message_185', 'message_197', 'message_198', 'message_201', 'message_205', 'message_208', 'message_215']
for mid in unclass_ids[:12]:
    print(mid, df_msg.loc[mid, 'user_id'], df_msg.loc[mid, 'source_type'])
    print('  ', df_msg.loc[mid, 'message_text'])
