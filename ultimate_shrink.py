import pickle
import os

print("Stripping massive redundant data from models...")

# 1. Strip the 50MB dataframe out of the ML models
for filename in ['collaborative.pkl', 'matrix_factorization.pkl']:
    filepath = f'models/{filename}'
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        if 'movies_df' in data:
            del data['movies_df']  # Deletes the redundant 50MB weight
            
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        print(f"✓ Shrunk {filename} to fit on GitHub")

# 2. Delete the original massive content_based matrix
if os.path.exists('models/content_based.pkl'):
    os.remove('models/content_based.pkl')
    print("✓ Removed old massive content_based.pkl")

print("✅ All files are now safely under the 100MB GitHub limit!")