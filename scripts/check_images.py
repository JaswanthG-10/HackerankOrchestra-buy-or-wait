import os
import pandas as pd

df_img = pd.read_csv('dataset/images.csv')
print(df_img)
for idx, r in df_img.iterrows():
    img_name = str(r['image_id']) + '.png'
    img_path = os.path.join('dataset', 'media', 'images', img_name)
    exists = os.path.exists(img_path)
    size = os.path.getsize(img_path) if exists else 0
    print(r['image_id'], img_path, 'exists:', exists, 'size:', size)
