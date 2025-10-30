"""
Big Data Food Analytics - Data Preprocessing Script
Purpose: Clean and reduce dataset to 450 MB for MongoDB Atlas upload
Author: Big Data Project
Date: October 29, 2025
"""

import pandas as pd
import json
import os
from datetime import datetime

print("=" * 70)
print("🥗 FOOD DATA PREPROCESSING FOR MONGODB ATLAS")
print("=" * 70)

# Configuration
INPUT_FILE = r"c:\Users\gokulp\Desktop\bigdata_tools\archive (17)\en.openfoodfacts.org.products.tsv"
OUTPUT_JSON = r"c:\Users\gokulp\Desktop\bigdata_tools\cleaned_food_data.json"
TARGET_RECORDS = 166288  # For ~450 MB
TARGET_SIZE_MB = 450

print(f"\n📁 Input File: {INPUT_FILE}")
print(f"🎯 Target Records: {TARGET_RECORDS:,}")
print(f"💾 Target Size: {TARGET_SIZE_MB} MB")
print(f"📤 Output File: {OUTPUT_JSON}")

# Step 1: Load the dataset
print("\n" + "=" * 70)
print("STEP 1: Loading Dataset...")
print("=" * 70)

try:
    # Read TSV file with selected columns only
    # Select only the most important nutritional and categorical columns
    selected_columns = [
        'code',
        'product_name',
        'brands',
        'categories',
        'categories_tags',
        'countries',
        'countries_tags',
        'ingredients_text',
        'allergens',
        'additives_tags',
        'serving_size',
        'energy_100g',
        'fat_100g',
        'saturated-fat_100g',
        'carbohydrates_100g',
        'sugars_100g',
        'fiber_100g',
        'proteins_100g',
        'salt_100g',
        'sodium_100g',
        'nutrition-score-fr_100g'
    ]
    
    print(f"📊 Reading TSV file (this may take a few minutes)...")
    df = pd.read_csv(INPUT_FILE, 
                     sep='\t', 
                     usecols=selected_columns,
                     low_memory=False,
                     encoding='utf-8',
                     on_bad_lines='skip')
    
    print(f"✅ Loaded {len(df):,} records")
    print(f"✅ Selected {len(selected_columns)} key columns")
    
except Exception as e:
    print(f"❌ Error loading file: {e}")
    exit(1)

# Step 2: Data Cleaning
print("\n" + "=" * 70)
print("STEP 2: Data Cleaning...")
print("=" * 70)

original_count = len(df)
print(f"📊 Original records: {original_count:,}")

# Remove rows where product_name is missing
df = df[df['product_name'].notna()]
print(f"✅ After removing null product names: {len(df):,} records")

# Remove rows where ALL nutritional values are missing
nutrition_cols = ['energy_100g', 'fat_100g', 'carbohydrates_100g', 'sugars_100g', 'proteins_100g']
df = df[df[nutrition_cols].notna().any(axis=1)]
print(f"✅ After removing records with no nutritional data: {len(df):,} records")

# Remove duplicate products (based on product code)
df = df.drop_duplicates(subset=['code'], keep='first')
print(f"✅ After removing duplicates: {len(df):,} records")

# Fill missing numerical values with 0
for col in nutrition_cols:
    df[col] = df[col].fillna(0)

# Fill missing text fields with empty string
text_cols = ['brands', 'categories', 'countries', 'ingredients_text', 'allergens', 'additives_tags']
for col in text_cols:
    df[col] = df[col].fillna('')

print(f"✅ Cleaned missing values")

# Step 3: Random Sampling
print("\n" + "=" * 70)
print("STEP 3: Random Sampling to Target Size...")
print("=" * 70)

if len(df) > TARGET_RECORDS:
    df_sampled = df.sample(n=TARGET_RECORDS, random_state=42)
    print(f"✅ Randomly sampled {TARGET_RECORDS:,} records from {len(df):,}")
else:
    df_sampled = df
    print(f"ℹ️  Dataset already has {len(df):,} records (less than target)")

# Step 4: Data Type Conversion
print("\n" + "=" * 70)
print("STEP 4: Converting Data Types...")
print("=" * 70)

# Convert numeric columns to proper types
numeric_cols = ['energy_100g', 'fat_100g', 'saturated-fat_100g', 
                'carbohydrates_100g', 'sugars_100g', 'fiber_100g', 
                'proteins_100g', 'salt_100g', 'sodium_100g', 'nutrition-score-fr_100g']

for col in numeric_cols:
    df_sampled[col] = pd.to_numeric(df_sampled[col], errors='coerce').fillna(0)

print(f"✅ Converted numerical columns")

# Step 5: Export to JSON
print("\n" + "=" * 70)
print("STEP 5: Exporting to JSON...")
print("=" * 70)

try:
    # Convert to JSON
    df_sampled.to_json(OUTPUT_JSON, orient='records', indent=2, force_ascii=False)
    
    # Get file size
    file_size_mb = os.path.getsize(OUTPUT_JSON) / (1024 * 1024)
    
    print(f"✅ Successfully exported to: {OUTPUT_JSON}")
    print(f"✅ Total records: {len(df_sampled):,}")
    print(f"✅ File size: {file_size_mb:.2f} MB")
    
except Exception as e:
    print(f"❌ Error exporting file: {e}")
    exit(1)

# Step 6: Generate Summary Report
print("\n" + "=" * 70)
print("📊 PREPROCESSING SUMMARY")
print("=" * 70)

print(f"\n📈 Data Reduction:")
print(f"   • Original records: {original_count:,}")
print(f"   • Final records: {len(df_sampled):,}")
print(f"   • Reduction: {((original_count - len(df_sampled)) / original_count * 100):.2f}%")

print(f"\n💾 File Information:")
print(f"   • Output file: cleaned_food_data.json")
print(f"   • File size: {file_size_mb:.2f} MB")
print(f"   • Columns: {len(selected_columns)}")

print(f"\n🔢 Nutritional Data Summary:")
print(f"   • Average Energy: {df_sampled['energy_100g'].mean():.2f} kcal")
print(f"   • Average Sugar: {df_sampled['sugars_100g'].mean():.2f} g")
print(f"   • Average Fat: {df_sampled['fat_100g'].mean():.2f} g")
print(f"   • Average Protein: {df_sampled['proteins_100g'].mean():.2f} g")

print(f"\n🌍 Top 5 Countries:")
country_counts = df_sampled['countries'].value_counts().head(5)
for country, count in country_counts.items():
    if country:
        print(f"   • {country}: {count:,} products")

print("\n" + "=" * 70)
print("✅ PREPROCESSING COMPLETE!")
print("=" * 70)
print(f"\n🚀 Next Steps:")
print(f"   1. Verify the output file: cleaned_food_data.json")
print(f"   2. Import to MongoDB Atlas using:")
print(f"      mongoimport --uri 'your_mongodb_atlas_uri'")
print(f"                  --collection food_items")
print(f"                  --file cleaned_food_data.json")
print(f"                  --jsonArray")
print(f"\n📌 File ready for MongoDB Atlas upload!")
print("=" * 70)
