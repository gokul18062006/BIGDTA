"""
MongoDB Quick Analysis Summary
Purpose: Generate quick insights from MongoDB Atlas data
"""

from pymongo import MongoClient

# MongoDB Connection
MONGO_URI = "mongodb+srv://gokulp1806official_db_user:6382253529gokul@nutrix.jicao8u.mongodb.net/"

print("=" * 70)
print("📊 MONGODB ATLAS - QUICK DATA SUMMARY")
print("=" * 70)

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
    db = client['FoodAnalytics']
    collection = db['food_items']
    
    print("\n✅ Connected to MongoDB Atlas!")
    
    # Basic Statistics
    print("\n" + "=" * 70)
    print("📈 BASIC STATISTICS")
    print("=" * 70)
    
    total = collection.count_documents({})
    print(f"✅ Total Documents: {total:,}")
    
    # Sample document
    sample = collection.find_one()
    if sample:
        print(f"\n📄 Sample Document Fields:")
        for key in sample.keys():
            if key != '_id':
                print(f"   • {key}")
    
    # Quick aggregations
    print("\n" + "=" * 70)
    print("🔢 NUTRITIONAL AVERAGES (All Products)")
    print("=" * 70)
    
    pipeline = [
        {"$group": {
            "_id": None,
            "avg_energy": {"$avg": "$energy_100g"},
            "avg_fat": {"$avg": "$fat_100g"},
            "avg_sugar": {"$avg": "$sugars_100g"},
            "avg_protein": {"$avg": "$proteins_100g"},
            "max_energy": {"$max": "$energy_100g"},
            "max_sugar": {"$max": "$sugars_100g"}
        }}
    ]
    
    result = list(collection.aggregate(pipeline))
    if result:
        stats = result[0]
        print(f"   • Average Energy: {stats['avg_energy']:.2f} kcal")
        print(f"   • Average Fat: {stats['avg_fat']:.2f} g")
        print(f"   • Average Sugar: {stats['avg_sugar']:.2f} g")
        print(f"   • Average Protein: {stats['avg_protein']:.2f} g")
        print(f"   • Max Energy: {stats['max_energy']:.0f} kcal")
        print(f"   • Max Sugar: {stats['max_sugar']:.0f} g")
    
    # Country distribution
    print("\n" + "=" * 70)
    print("🌍 TOP 5 COUNTRIES BY PRODUCT COUNT")
    print("=" * 70)
    
    pipeline_countries = [
        {"$match": {"countries": {"$ne": ""}}},
        {"$group": {"_id": "$countries", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    
    countries = list(collection.aggregate(pipeline_countries))
    for i, doc in enumerate(countries, 1):
        print(f"   {i}. {doc['_id']:30} - {doc['count']:,} products")
    
    print("\n" + "=" * 70)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 70)
    print("\n💡 Your MongoDB Atlas database is successfully set up and ready!")
    print("   • Database: FoodAnalytics")
    print("   • Collection: food_items")
    print("   • Documents: {:,}".format(total))
    
    client.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n💡 If connection timed out, your Atlas cluster may be paused.")
    print("   Go to MongoDB Atlas dashboard and ensure cluster is active.")
