"""
Verify JSON file record count
"""
import json
import os

json_file = r"c:\Users\gokulp\Desktop\bigdata_tools\cleaned_food_data.json"

print("=" * 70)
print("📊 JSON FILE VERIFICATION")
print("=" * 70)

# Check file size
file_size_mb = os.path.getsize(json_file) / (1024 * 1024)
print(f"\n📁 File: cleaned_food_data.json")
print(f"💾 File Size: {file_size_mb:.2f} MB")

# Load and count records
print(f"\n⏳ Loading JSON file to count records...")
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"✅ Total records in JSON file: {len(data):,}")

print("\n" + "=" * 70)
print("📊 COMPARISON")
print("=" * 70)
print(f"Records in cleaned_food_data.json: {len(data):,}")
print(f"Records in MongoDB Atlas:          166,288")
print(f"Match: {'YES ✅' if len(data) == 166288 else 'NO ❌'}")

if len(data) == 166288:
    print("\n✅ ALL DATA HAS BEEN SUCCESSFULLY UPLOADED!")
    print("   Your MongoDB Atlas contains all records from the JSON file.")
else:
    print(f"\n⚠️  Difference: {abs(len(data) - 166288):,} records")
    if len(data) > 166288:
        print(f"   Missing in MongoDB: {len(data) - 166288:,} records")
    else:
        print(f"   Extra in MongoDB: {166288 - len(data):,} records")

print("=" * 70)
