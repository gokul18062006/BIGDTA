"""
MongoDB Atlas Import Script
Purpose: Import cleaned food data to MongoDB Atlas
Date: October 29, 2025
"""

import json
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from datetime import datetime
import os

print("=" * 70)
print("🍃 MONGODB ATLAS DATA IMPORT")
print("=" * 70)

# Configuration
MONGO_URI = "mongodb+srv://gokulp1806official_db_user:6382253529gokul@nutrix.jicao8u.mongodb.net/"
DATABASE_NAME = "FoodAnalytics"
COLLECTION_NAME = "food_items"
JSON_FILE = r"c:\Users\gokulp\Desktop\bigdata_tools\cleaned_food_data.json"

print(f"\n📡 Connecting to MongoDB Atlas...")
print(f"🗄️  Database: {DATABASE_NAME}")
print(f"📦 Collection: {COLLECTION_NAME}")
print(f"📁 Data File: {JSON_FILE}")

# Step 1: Test Connection
print("\n" + "=" * 70)
print("STEP 1: Testing MongoDB Atlas Connection...")
print("=" * 70)

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Test connection
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!")
    
except ConnectionFailure as e:
    print(f"❌ Connection failed: {e}")
    print("\n💡 Troubleshooting:")
    print("   1. Check your internet connection")
    print("   2. Verify MongoDB Atlas IP whitelist (allow 0.0.0.0/0 for testing)")
    print("   3. Confirm username and password are correct")
    exit(1)
except ServerSelectionTimeoutError as e:
    print(f"❌ Connection timeout: {e}")
    print("\n💡 Check your MongoDB Atlas cluster status")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    exit(1)

# Step 2: Select Database and Collection
print("\n" + "=" * 70)
print("STEP 2: Setting up Database and Collection...")
print("=" * 70)

db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Check if collection already exists and has data
existing_count = collection.count_documents({})
if existing_count > 0:
    print(f"⚠️  Collection '{COLLECTION_NAME}' already contains {existing_count:,} documents")
    response = input("❓ Do you want to DROP existing data and import fresh? (yes/no): ").strip().lower()
    if response == 'yes':
        print("🗑️  Dropping existing collection...")
        collection.drop()
        print("✅ Collection dropped")
    else:
        print("⏭️  Skipping import. Existing data will be kept.")
        exit(0)
else:
    print(f"✅ Collection '{COLLECTION_NAME}' is ready for data import")

# Step 3: Load JSON Data
print("\n" + "=" * 70)
print("STEP 3: Loading JSON Data...")
print("=" * 70)

try:
    if not os.path.exists(JSON_FILE):
        print(f"❌ File not found: {JSON_FILE}")
        exit(1)
    
    file_size_mb = os.path.getsize(JSON_FILE) / (1024 * 1024)
    print(f"📊 File size: {file_size_mb:.2f} MB")
    print(f"⏳ Loading data (this may take a minute)...")
    
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data):,} records from JSON file")
    
except json.JSONDecodeError as e:
    print(f"❌ Invalid JSON format: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Error loading file: {e}")
    exit(1)

# Step 4: Import Data to MongoDB Atlas
print("\n" + "=" * 70)
print("STEP 4: Importing Data to MongoDB Atlas...")
print("=" * 70)

try:
    print(f"⏳ Inserting {len(data):,} documents (this may take 2-3 minutes)...")
    
    # Insert in batches for better performance
    BATCH_SIZE = 1000
    total_batches = (len(data) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for i in range(0, len(data), BATCH_SIZE):
        batch = data[i:i + BATCH_SIZE]
        collection.insert_many(batch, ordered=False)
        current_batch = (i // BATCH_SIZE) + 1
        progress = (current_batch / total_batches) * 100
        print(f"   📤 Progress: Batch {current_batch}/{total_batches} ({progress:.1f}%)")
    
    print(f"✅ Successfully imported {len(data):,} documents!")
    
except Exception as e:
    print(f"❌ Error during import: {e}")
    exit(1)

# Step 5: Verify Import
print("\n" + "=" * 70)
print("STEP 5: Verifying Import...")
print("=" * 70)

try:
    # Count documents
    doc_count = collection.count_documents({})
    print(f"✅ Total documents in collection: {doc_count:,}")
    
    # Get sample document
    sample = collection.find_one()
    if sample:
        print(f"\n📄 Sample Document:")
        print(f"   • Product: {sample.get('product_name', 'N/A')}")
        print(f"   • Brand: {sample.get('brands', 'N/A')}")
        print(f"   • Country: {sample.get('countries', 'N/A')}")
        print(f"   • Energy: {sample.get('energy_100g', 'N/A')} kcal")
        print(f"   • Sugar: {sample.get('sugars_100g', 'N/A')} g")
        print(f"   • Fat: {sample.get('fat_100g', 'N/A')} g")
    
    # Get database stats
    stats = db.command("collstats", COLLECTION_NAME)
    size_mb = stats['size'] / (1024 * 1024)
    print(f"\n💾 Collection Storage:")
    print(f"   • Size: {size_mb:.2f} MB")
    print(f"   • Average Document Size: {stats.get('avgObjSize', 0)} bytes")
    
except Exception as e:
    print(f"❌ Error verifying import: {e}")

# Step 6: Create Indexes for Performance
print("\n" + "=" * 70)
print("STEP 6: Creating Indexes for Better Performance...")
print("=" * 70)

try:
    # Create indexes on frequently queried fields
    collection.create_index("product_name")
    collection.create_index("categories")
    collection.create_index("countries")
    collection.create_index("energy_100g")
    collection.create_index("sugars_100g")
    collection.create_index("fat_100g")
    
    print("✅ Created indexes on key fields:")
    print("   • product_name")
    print("   • categories")
    print("   • countries")
    print("   • energy_100g, sugars_100g, fat_100g")
    
except Exception as e:
    print(f"⚠️  Warning: Could not create indexes: {e}")

# Final Summary
print("\n" + "=" * 70)
print("🎉 IMPORT COMPLETE!")
print("=" * 70)

print(f"\n✅ Successfully imported {doc_count:,} food products to MongoDB Atlas")
print(f"\n📊 Database Details:")
print(f"   • URI: {MONGO_URI[:50]}...")
print(f"   • Database: {DATABASE_NAME}")
print(f"   • Collection: {COLLECTION_NAME}")
print(f"   • Documents: {doc_count:,}")
print(f"   • Storage Size: {size_mb:.2f} MB")

print(f"\n🚀 Next Steps:")
print(f"   1. Verify data in MongoDB Atlas dashboard")
print(f"   2. Run MapReduce queries for analysis")
print(f"   3. Create visualizations from aggregated data")

print(f"\n💡 Quick Test Query (in MongoDB Shell or Compass):")
print(f"   db.{COLLECTION_NAME}.find().limit(5)")
print(f"   db.{COLLECTION_NAME}.countDocuments({{}})")

print("\n" + "=" * 70)

# Close connection
client.close()
print("✅ Connection closed successfully")
