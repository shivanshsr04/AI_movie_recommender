"""
Diagnostic Script - Check Your Movie Data Structure
Run this to see what columns your dataframe actually has
"""

import pickle
import pandas as pd

print("=" * 80)
print("🔍 DIAGNOSTIC: CHECKING YOUR MOVIE DATA")
print("=" * 80)

# Try to load your cleaned data
file_path = 'models/clean_movies.pkl'

try:
    print(f"\n📁 Loading from: {file_path}")
    with open(file_path, 'rb') as f:
        movies_df = pickle.load(f)
    
    print("✅ Data loaded successfully!")
    print(f"\n📊 Dataset Shape: {movies_df.shape}")
    print(f"   - Rows (movies): {movies_df.shape[0]:,}")
    print(f"   - Columns: {movies_df.shape[1]}")
    
    print("\n📋 COLUMN NAMES:")
    print("=" * 80)
    for i, col in enumerate(movies_df.columns, 1):
        print(f"  {i:2d}. {col:30s} (dtype: {movies_df[col].dtype})")
    
    print("\n📊 FIRST ROW PREVIEW:")
    print("=" * 80)
    print(movies_df.iloc[0])
    
    print("\n🔍 CHECKING SPECIFIC COLUMNS:")
    print("=" * 80)
    
    # Check for year/date columns
    year_cols = [col for col in movies_df.columns if 'year' in col.lower() or 'date' in col.lower() or 'release' in col.lower()]
    if year_cols:
        print(f"✅ Year/Date columns found: {year_cols}")
    else:
        print(f"❌ No year/date columns found")
    
    # Check for title column
    title_cols = [col for col in movies_df.columns if 'title' in col.lower() or 'name' in col.lower()]
    if title_cols:
        print(f"✅ Title columns found: {title_cols}")
    else:
        print(f"❌ No title columns found")
    
    # Check for rating column
    rating_cols = [col for col in movies_df.columns if 'rating' in col.lower() or 'vote' in col.lower() or 'score' in col.lower()]
    if rating_cols:
        print(f"✅ Rating columns found: {rating_cols}")
    else:
        print(f"❌ No rating columns found")
    
    # Check for popularity column
    popularity_cols = [col for col in movies_df.columns if 'popular' in col.lower()]
    if popularity_cols:
        print(f"✅ Popularity columns found: {popularity_cols}")
    else:
        print(f"❌ No popularity columns found")
    
    # Check for overview/description
    overview_cols = [col for col in movies_df.columns if 'overview' in col.lower() or 'description' in col.lower() or 'synopsis' in col.lower()]
    if overview_cols:
        print(f"✅ Overview columns found: {overview_cols}")
    else:
        print(f"❌ No overview columns found")
    
    print("\n📝 SAMPLE DATA (First 5 rows):")
    print("=" * 80)
    print(movies_df.head())
    
    print("\n✅ DIAGNOSTIC COMPLETE!")
    print("\n💡 NEXT STEP:")
    print("Look at the column names above and update your streamlit_app.py")
    print("Replace 'year' with the actual column name from this list")
    print("Replace 'title' with the actual column name from this list")
    print("Replace 'vote_average' with the actual column name from this list")
    print("Replace 'popularity' with the actual column name from this list")
    
except FileNotFoundError:
    print(f"❌ File not found: {file_path}")
    print("\n📍 Please make sure your cleaned data exists at: models/clean_movies.pkl")
    print("\n💡 To create it, run: python train_models.py")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    print(f"\n📍 Error type: {type(e).__name__}")
    import traceback
    print(f"\n📋 Full traceback:")
    traceback.print_exc()

print("\n" + "=" * 80)