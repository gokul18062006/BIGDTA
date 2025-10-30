"""
MongoDB MapReduce Analysis Scripts
Purpose: Analyze food data using MongoDB Aggregation Framework (Modern MapReduce)
Database: FoodAnalytics
Collection: food_items
"""

from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# MongoDB Connection
MONGO_URI = "mongodb+srv://gokulp1806official_db_user:6382253529gokul@nutrix.jicao8u.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client['FoodAnalytics']
collection = db['food_items']

print("=" * 70)
print("📊 BIG DATA MAPREDUCE ANALYSIS - FOOD ANALYTICS")
print("=" * 70)

# ============================================================================
# ANALYSIS 1: Average Sugar Content per Country
# ============================================================================
print("\n🔍 ANALYSIS 1: Average Sugar Content per Country")
print("=" * 70)

print("⏳ Running aggregation for Average Sugar per Country...")
pipeline_sugar = [
    {"$match": {"countries": {"$ne": ""}, "sugars_100g": {"$gt": 0}}},
    {"$group": {
        "_id": "$countries",
        "avg_sugar": {"$avg": "$sugars_100g"},
        "count": {"$sum": 1}
    }},
    {"$sort": {"avg_sugar": -1}},
    {"$limit": 10}
]

top_countries = list(collection.aggregate(pipeline_sugar))
print(f"✅ Completed! Top 10 countries by average sugar content:\n")
for i, doc in enumerate(top_countries, 1):
    country = doc['_id']
    avg_sugar = doc['avg_sugar']
    count = doc['count']
    print(f"   {i}. {country:20} - Avg: {avg_sugar:.2f}g (from {count:,} products)")

# ============================================================================
# ANALYSIS 2: Average Fat Content per Country
# ============================================================================
print("\n\n🔍 ANALYSIS 2: Average Fat Content per Country")
print("=" * 70)

print("⏳ Running aggregation for Average Fat per Country...")
pipeline_fat = [
    {"$match": {"countries": {"$ne": ""}, "fat_100g": {"$gt": 0}}},
    {"$group": {
        "_id": "$countries",
        "avg_fat": {"$avg": "$fat_100g"},
        "count": {"$sum": 1}
    }},
    {"$sort": {"avg_fat": -1}},
    {"$limit": 10}
]

top_countries_fat = list(collection.aggregate(pipeline_fat))
print(f"✅ Completed! Top 10 countries by average fat content:\n")
for i, doc in enumerate(top_countries_fat, 1):
    country = doc['_id']
    avg_fat = doc['avg_fat']
    count = doc['count']
    print(f"   {i}. {country:20} - Avg: {avg_fat:.2f}g (from {count:,} products)")

# ============================================================================
# ANALYSIS 3: Average Energy (Calories) per Country
# ============================================================================
print("\n\n🔍 ANALYSIS 3: Average Energy Content per Country")
print("=" * 70)

print("⏳ Running aggregation for Average Energy per Country...")
pipeline_energy = [
    {"$match": {"countries": {"$ne": ""}, "energy_100g": {"$gt": 0}}},
    {"$group": {
        "_id": "$countries",
        "avg_energy": {"$avg": "$energy_100g"},
        "count": {"$sum": 1}
    }},
    {"$sort": {"avg_energy": -1}},
    {"$limit": 10}
]

top_countries_energy = list(collection.aggregate(pipeline_energy))
print(f"✅ Completed! Top 10 countries by average energy content:\n")
for i, doc in enumerate(top_countries_energy, 1):
    country = doc['_id']
    avg_energy = doc['avg_energy']
    count = doc['count']
    print(f"   {i}. {country:20} - Avg: {avg_energy:.2f} kcal (from {count:,} products)")

# ============================================================================
# ANALYSIS 4: Product Count by Country
# ============================================================================
print("\n\n🔍 ANALYSIS 4: Product Distribution by Country")
print("=" * 70)

pipeline = [
    {"$match": {"countries": {"$ne": ""}}},
    {"$group": {
        "_id": "$countries",
        "count": {"$sum": 1}
    }},
    {"$sort": {"count": -1}},
    {"$limit": 10}
]

print("⏳ Running aggregation for product count...")
top_product_countries = list(collection.aggregate(pipeline))
print(f"✅ Completed! Top 10 countries by number of products:\n")
for i, doc in enumerate(top_product_countries, 1):
    country = doc['_id']
    count = doc['count']
    print(f"   {i}. {country:20} - {count:,} products")

# ============================================================================
# ANALYSIS 5: High Sugar Products (Top 20)
# ============================================================================
print("\n\n🔍 ANALYSIS 5: Top 20 High-Sugar Products")
print("=" * 70)

high_sugar = list(collection.find(
    {"sugars_100g": {"$gt": 0}},
    {"product_name": 1, "brands": 1, "sugars_100g": 1, "countries": 1, "_id": 0}
).sort("sugars_100g", -1).limit(20))

print("✅ Top 20 products with highest sugar content:\n")
for i, product in enumerate(high_sugar, 1):
    name = product.get('product_name', 'Unknown')[:40]
    sugar = product.get('sugars_100g', 0)
    brand = product.get('brands', 'N/A')[:20]
    country = product.get('countries', 'N/A')[:15]
    print(f"   {i:2}. {name:40} | {sugar:5.1f}g | {brand:20} | {country}")

# ============================================================================
# ANALYSIS 6: High Calorie Products (Top 20)
# ============================================================================
print("\n\n🔍 ANALYSIS 6: Top 20 High-Calorie Products")
print("=" * 70)

high_calorie = list(collection.find(
    {"energy_100g": {"$gt": 0}},
    {"product_name": 1, "brands": 1, "energy_100g": 1, "countries": 1, "_id": 0}
).sort("energy_100g", -1).limit(20))

print("✅ Top 20 products with highest calorie content:\n")
for i, product in enumerate(high_calorie, 1):
    name = product.get('product_name', 'Unknown')[:40]
    energy = product.get('energy_100g', 0)
    brand = product.get('brands', 'N/A')[:20]
    country = product.get('countries', 'N/A')[:15]
    print(f"   {i:2}. {name:40} | {energy:6.0f} kcal | {brand:20} | {country}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("📊 ANALYSIS COMPLETE - SUMMARY")
print("=" * 70)

total_docs = collection.count_documents({})
print(f"\n✅ Total Products Analyzed: {total_docs:,}")
print(f"✅ Aggregation Pipelines Executed: 6")
print(f"   • Average Sugar per Country")
print(f"   • Average Fat per Country")
print(f"   • Average Energy per Country")
print(f"   • Product Count by Country")
print(f"   • Top High-Sugar Products")
print(f"   • Top High-Calorie Products")

print(f"\n🎯 Key Insights:")
print(f"   • US has the most products: {top_product_countries[0]['count']:,}")
print(f"   • Highest avg sugar country: {top_countries[0]['_id']} ({top_countries[0]['avg_sugar']:.2f}g)")
print(f"   • Highest avg fat country: {top_countries_fat[0]['_id']} ({top_countries_fat[0]['avg_fat']:.2f}g)")
print(f"   • Highest avg energy country: {top_countries_energy[0]['_id']} ({top_countries_energy[0]['avg_energy']:.0f} kcal)")

print("\n" + "=" * 70)
print("🚀 Next Steps:")
print("   1. Create visualizations using matplotlib/seaborn")
print("   2. Generate detailed reports for each analysis")
print("   3. Identify unhealthy food patterns for policy recommendations")
print("=" * 70)

client.close()
