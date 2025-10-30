"""
🥗 Big Data Food Analytics Dashboard
Streamlit Web Application for Interactive Data Visualization
Author: Big Data Project Team
Date: October 29, 2025
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pymongo import MongoClient
import warnings

warnings.filterwarnings('ignore')

# Page Configuration
st.set_page_config(
    page_title="Food Analytics Dashboard",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .stMetric label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #1f77b4 !important;
        font-size: 2rem !important;
        font-weight: bold !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: #27ae60 !important;
        font-weight: 500 !important;
    }
    h1 {
        color: #2c3e50;
        font-weight: bold;
    }
    h2 {
        color: #34495e;
    }
    h3 {
        color: #7f8c8d;
    }
    .stAlert {
        background-color: #d5f4e6;
        border-left: 5px solid #27ae60;
    }
    div[data-testid="stMarkdownContainer"] p {
        color: #2c3e50;
    }
    .sidebar .sidebar-content {
        background-color: #2c3e50;
    }
    [data-testid="stSidebar"] {
        background-color: #2c3e50;
    }
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] p {
        color: #ecf0f1 !important;
    }
    section[data-testid="stSidebar"] > div {
        background-color: #2c3e50;
    }
    </style>
""", unsafe_allow_html=True)

# MongoDB Connection
@st.cache_resource
def init_mongodb_connection():
    """Initialize MongoDB connection"""
    try:
        MONGO_URI = "mongodb+srv://gokulp1806official_db_user:6382253529gokul@nutrix.jicao8u.mongodb.net/"
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
        client.admin.command('ping')
        return client
    except Exception as e:
        st.error(f"❌ MongoDB Connection Failed: {e}")
        return None

# Load data from MongoDB
def load_data_from_mongodb():
    """Load and cache data from MongoDB"""
    client = init_mongodb_connection()
    if client is None:
        return None, None, None
    
    db = client['FoodAnalytics']
    collection = db['food_items']
    
    # Load sample data
    data = list(collection.find().limit(10000))  # Load 10k for faster performance
    df = pd.DataFrame(data)
    
    return df, collection, client

# Perform aggregation analyses
@st.cache_data(ttl=3600)
def get_sugar_analysis(_collection):
    """Get average sugar content by country"""
    pipeline = [
        {"$match": {"countries": {"$ne": "", "$exists": True}, "sugars_100g": {"$gt": 0}}},
        {"$group": {
            "_id": "$countries",
            "avg_sugar": {"$avg": "$sugars_100g"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"avg_sugar": -1}},
        {"$limit": 15}
    ]
    results = list(_collection.aggregate(pipeline))
    return pd.DataFrame(results)

@st.cache_data(ttl=3600)
def get_fat_analysis(_collection):
    """Get average fat content by country"""
    pipeline = [
        {"$match": {"countries": {"$ne": "", "$exists": True}, "fat_100g": {"$gt": 0}}},
        {"$group": {
            "_id": "$countries",
            "avg_fat": {"$avg": "$fat_100g"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"avg_fat": -1}},
        {"$limit": 15}
    ]
    results = list(_collection.aggregate(pipeline))
    return pd.DataFrame(results)

@st.cache_data(ttl=3600)
def get_energy_analysis(_collection):
    """Get average energy content by country"""
    pipeline = [
        {"$match": {"countries": {"$ne": "", "$exists": True}, "energy_100g": {"$gt": 0, "$lt": 10000}}},
        {"$group": {
            "_id": "$countries",
            "avg_energy": {"$avg": "$energy_100g"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"avg_energy": -1}},
        {"$limit": 15}
    ]
    results = list(_collection.aggregate(pipeline))
    return pd.DataFrame(results)

@st.cache_data(ttl=3600)
def get_distribution_analysis(_collection):
    """Get product distribution by country"""
    pipeline = [
        {"$match": {"countries": {"$ne": "", "$exists": True}}},
        {"$group": {"_id": "$countries", "product_count": {"$sum": 1}}},
        {"$sort": {"product_count": -1}},
        {"$limit": 10}
    ]
    results = list(_collection.aggregate(pipeline))
    return pd.DataFrame(results)

@st.cache_data(ttl=3600)
def get_high_sugar_products(_collection):
    """Get high sugar products"""
    products = list(_collection.find(
        {"sugars_100g": {"$gt": 0}},
        {"product_name": 1, "brands": 1, "sugars_100g": 1, "countries": 1, "_id": 0}
    ).sort("sugars_100g", -1).limit(20))
    return pd.DataFrame(products)

@st.cache_data(ttl=3600)
def get_high_calorie_products(_collection):
    """Get high calorie products"""
    products = list(_collection.find(
        {"energy_100g": {"$gt": 0, "$lt": 10000}},
        {"product_name": 1, "brands": 1, "energy_100g": 1, "countries": 1, "_id": 0}
    ).sort("energy_100g", -1).limit(20))
    return pd.DataFrame(products)

# Main Dashboard
def main():
    # Header
    st.title("🥗 Big Data Analytics for Smarter Food Choices")
    st.markdown("### Interactive Dashboard - Real-time Food Nutrition Analysis")
    st.markdown("---")
    
    # Load data
    with st.spinner("🔄 Connecting to MongoDB Atlas and loading data..."):
        result = load_data_from_mongodb()
        
    if result is None or result[0] is None:
        st.error("❌ Failed to connect to MongoDB. Please check your connection.")
        return
    
    df, collection, client = result
    total_docs = collection.count_documents({})
    
    # Sidebar
    st.sidebar.header("📊 Dashboard Controls")
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigate to:",
        ["🏠 Overview", "📈 Nutritional Analysis", "🌍 Geographic Insights", 
         "⚠️ High-Risk Products", "📊 Data Explorer", "💡 Insights & Recommendations"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"**Total Products:** {total_docs:,}")
    st.sidebar.success("✅ Connected to MongoDB Atlas")
    
    # Page routing
    if page == "🏠 Overview":
        show_overview(df, collection, total_docs)
    elif page == "📈 Nutritional Analysis":
        show_nutritional_analysis(collection)
    elif page == "🌍 Geographic Insights":
        show_geographic_insights(collection)
    elif page == "⚠️ High-Risk Products":
        show_high_risk_products(collection)
    elif page == "📊 Data Explorer":
        show_data_explorer(df)
    elif page == "💡 Insights & Recommendations":
        show_insights()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Project:** Big Data Food Analytics")
    st.sidebar.markdown("**Database:** MongoDB Atlas")
    st.sidebar.markdown("**Framework:** Streamlit + Plotly")

def show_overview(df, collection, total_docs):
    """Show overview page"""
    st.header("🏠 Project Overview")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Total Products", f"{total_docs:,}", "From 150+ Countries")
    
    with col2:
        avg_energy = df['energy_100g'].mean() if 'energy_100g' in df.columns else 0
        st.metric("⚡ Avg Energy", f"{avg_energy:.0f} kcal", "Per 100g")
    
    with col3:
        avg_sugar = df['sugars_100g'].mean() if 'sugars_100g' in df.columns else 0
        st.metric("🍬 Avg Sugar", f"{avg_sugar:.1f}g", "Per 100g")
    
    with col4:
        avg_fat = df['fat_100g'].mean() if 'fat_100g' in df.columns else 0
        st.metric("🥓 Avg Fat", f"{avg_fat:.1f}g", "Per 100g")
    
    st.markdown("---")
    
    # Project Description
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 About This Project")
        st.markdown("""
        This **Big Data Analytics** project analyzes **166,288 food products** from the Open Food Facts dataset 
        to help consumers make healthier food choices. Using MongoDB Atlas and MapReduce-style aggregations, 
        we uncover patterns in nutritional content across different countries and identify high-risk products.
        
        **Key Objectives:**
        - 🔍 Analyze large-scale food data using Big Data tools
        - 📊 Identify nutritional patterns and trends
        - ⚠️ Detect unhealthy dietary patterns
        - 💡 Provide data-driven health recommendations
        """)
    
    with col2:
        st.subheader("🛠️ Technologies Used")
        st.markdown("""
        - **Database:** MongoDB Atlas
        - **Analysis:** MapReduce Aggregation
        - **Visualization:** Plotly + Streamlit
        - **Language:** Python
        - **Data Processing:** Pandas, NumPy
        """)
    
    st.markdown("---")
    
    # Quick Stats
    st.subheader("📊 Quick Statistics")
    
    # Get top countries
    df_dist = get_distribution_analysis(collection)
    
    if not df_dist.empty:
        fig = px.bar(
            df_dist.head(10),
            x='_id',
            y='product_count',
            title='Top 10 Countries by Product Count',
            labels={'_id': 'Country', 'product_count': 'Number of Products'},
            color='product_count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def show_nutritional_analysis(collection):
    """Show nutritional analysis page"""
    st.header("📈 Nutritional Analysis by Country")
    st.markdown("MapReduce-based aggregation analysis of nutritional content")
    st.markdown("---")
    
    # Tabs for different nutrients
    tab1, tab2, tab3 = st.tabs(["🍬 Sugar Content", "🥓 Fat Content", "⚡ Energy Content"])
    
    with tab1:
        st.subheader("Average Sugar Content by Country")
        df_sugar = get_sugar_analysis(collection)
        
        if not df_sugar.empty:
            # Plotly chart
            fig = px.bar(
                df_sugar.head(10),
                x='_id',
                y='avg_sugar',
                title='Top 10 Countries by Average Sugar Content (per 100g)',
                labels={'_id': 'Country', 'avg_sugar': 'Average Sugar (g)'},
                color='avg_sugar',
                color_continuous_scale='Reds',
                text='avg_sugar'
            )
            fig.update_traces(texttemplate='%{text:.2f}g', textposition='outside')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Data table
            with st.expander("📊 View Detailed Data"):
                df_sugar['avg_sugar'] = df_sugar['avg_sugar'].round(2)
                st.dataframe(df_sugar.head(15), use_container_width=True)
    
    with tab2:
        st.subheader("Average Fat Content by Country")
        df_fat = get_fat_analysis(collection)
        
        if not df_fat.empty:
            fig = px.bar(
                df_fat.head(10),
                x='_id',
                y='avg_fat',
                title='Top 10 Countries by Average Fat Content (per 100g)',
                labels={'_id': 'Country', 'avg_fat': 'Average Fat (g)'},
                color='avg_fat',
                color_continuous_scale='Oranges',
                text='avg_fat'
            )
            fig.update_traces(texttemplate='%{text:.2f}g', textposition='outside')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("📊 View Detailed Data"):
                df_fat['avg_fat'] = df_fat['avg_fat'].round(2)
                st.dataframe(df_fat.head(15), use_container_width=True)
    
    with tab3:
        st.subheader("Average Energy Content by Country")
        df_energy = get_energy_analysis(collection)
        
        if not df_energy.empty:
            fig = px.bar(
                df_energy.head(10),
                x='_id',
                y='avg_energy',
                title='Top 10 Countries by Average Energy Content (per 100g)',
                labels={'_id': 'Country', 'avg_energy': 'Average Energy (kcal)'},
                color='avg_energy',
                color_continuous_scale='Greens',
                text='avg_energy'
            )
            fig.update_traces(texttemplate='%{text:.0f} kcal', textposition='outside')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("📊 View Detailed Data"):
                df_energy['avg_energy'] = df_energy['avg_energy'].round(2)
                st.dataframe(df_energy.head(15), use_container_width=True)

def show_geographic_insights(collection):
    """Show geographic insights page"""
    st.header("🌍 Geographic Distribution & Insights")
    st.markdown("Product distribution and nutritional patterns across countries")
    st.markdown("---")
    
    # Product Distribution
    st.subheader("📦 Product Distribution by Country")
    df_dist = get_distribution_analysis(collection)
    
    if not df_dist.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Pie chart
            fig = px.pie(
                df_dist.head(5),
                values='product_count',
                names='_id',
                title='Product Distribution - Top 5 Countries',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Top Countries")
            for i, row in df_dist.head(5).iterrows():
                st.metric(
                    row['_id'][:20],
                    f"{row['product_count']:,}",
                    f"{(row['product_count']/df_dist['product_count'].sum()*100):.1f}%"
                )
    
    st.markdown("---")
    
    # Comparison across countries
    st.subheader("🔬 Nutritional Comparison Across Top Countries")
    
    # Get data for top 5 countries
    top_countries = df_dist.head(5)['_id'].tolist() if not df_dist.empty else []
    
    if top_countries:
        nutrition_data = []
        for country in top_countries:
            pipeline = [
                {"$match": {"countries": country}},
                {"$group": {
                    "_id": country,
                    "avg_energy": {"$avg": "$energy_100g"},
                    "avg_sugar": {"$avg": "$sugars_100g"},
                    "avg_fat": {"$avg": "$fat_100g"},
                    "avg_protein": {"$avg": "$proteins_100g"}
                }}
            ]
            result = list(collection.aggregate(pipeline))
            if result:
                nutrition_data.append(result[0])
        
        if nutrition_data:
            df_nutrition = pd.DataFrame(nutrition_data)
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Energy (kcal)', 'Sugar (g)', 'Fat (g)', 'Protein (g)')
            )
            
            fig.add_trace(
                go.Bar(x=df_nutrition['_id'], y=df_nutrition['avg_energy'], name='Energy',
                       marker_color='indianred'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(x=df_nutrition['_id'], y=df_nutrition['avg_sugar'], name='Sugar',
                       marker_color='salmon'),
                row=1, col=2
            )
            
            fig.add_trace(
                go.Bar(x=df_nutrition['_id'], y=df_nutrition['avg_fat'], name='Fat',
                       marker_color='orange'),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Bar(x=df_nutrition['_id'], y=df_nutrition['avg_protein'], name='Protein',
                       marker_color='lightgreen'),
                row=2, col=2
            )
            
            fig.update_layout(height=600, showlegend=False, title_text="Nutritional Comparison")
            st.plotly_chart(fig, use_container_width=True)

def show_high_risk_products(collection):
    """Show high-risk products page"""
    st.header("⚠️ High-Risk Products Identification")
    st.markdown("Products with dangerously high sugar, fat, or calorie content")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🍬 High-Sugar Products", "⚡ High-Calorie Products"])
    
    with tab1:
        st.subheader("Top 20 Products with Highest Sugar Content")
        st.warning("⚠️ Products with >50g sugar per 100g are high-risk for diabetes and obesity")
        
        df_high_sugar = get_high_sugar_products(collection)
        
        if not df_high_sugar.empty:
            # Add ranking
            df_high_sugar['Rank'] = range(1, len(df_high_sugar) + 1)
            
            # Display as interactive table
            st.dataframe(
                df_high_sugar[['Rank', 'product_name', 'brands', 'sugars_100g', 'countries']].rename(
                    columns={
                        'product_name': 'Product Name',
                        'brands': 'Brand',
                        'sugars_100g': 'Sugar (g)',
                        'countries': 'Country'
                    }
                ),
                use_container_width=True,
                height=600
            )
            
            # Bar chart
            fig = px.bar(
                df_high_sugar.head(10),
                x='sugars_100g',
                y='product_name',
                orientation='h',
                title='Top 10 High-Sugar Products',
                labels={'sugars_100g': 'Sugar Content (g)', 'product_name': 'Product'},
                color='sugars_100g',
                color_continuous_scale='Reds'
            )
            fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Top 20 Products with Highest Calorie Content")
        st.warning("⚠️ Products with >500 kcal per 100g should be consumed in moderation")
        
        df_high_calorie = get_high_calorie_products(collection)
        
        if not df_high_calorie.empty:
            df_high_calorie['Rank'] = range(1, len(df_high_calorie) + 1)
            
            st.dataframe(
                df_high_calorie[['Rank', 'product_name', 'brands', 'energy_100g', 'countries']].rename(
                    columns={
                        'product_name': 'Product Name',
                        'brands': 'Brand',
                        'energy_100g': 'Energy (kcal)',
                        'countries': 'Country'
                    }
                ),
                use_container_width=True,
                height=600
            )
            
            # Bar chart
            fig = px.bar(
                df_high_calorie.head(10),
                x='energy_100g',
                y='product_name',
                orientation='h',
                title='Top 10 High-Calorie Products',
                labels={'energy_100g': 'Energy Content (kcal)', 'product_name': 'Product'},
                color='energy_100g',
                color_continuous_scale='Oranges'
            )
            fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

def show_data_explorer(df):
    """Show data explorer page"""
    st.header("📊 Data Explorer")
    st.markdown("Explore and filter the food products dataset")
    st.markdown("---")
    
    if df is not None and not df.empty:
        # Filters
        st.subheader("🔍 Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'countries' in df.columns:
                countries = ['All'] + sorted(df['countries'].dropna().unique().tolist())
                selected_country = st.selectbox("Country", countries)
        
        with col2:
            if 'sugars_100g' in df.columns:
                sugar_threshold = st.slider("Max Sugar (g)", 0, 100, 50)
        
        with col3:
            if 'energy_100g' in df.columns:
                energy_threshold = st.slider("Max Energy (kcal)", 0, 1000, 500)
        
        # Apply filters
        filtered_df = df.copy()
        if selected_country != 'All' and 'countries' in df.columns:
            filtered_df = filtered_df[filtered_df['countries'] == selected_country]
        if 'sugars_100g' in df.columns:
            filtered_df = filtered_df[filtered_df['sugars_100g'] <= sugar_threshold]
        if 'energy_100g' in df.columns:
            filtered_df = filtered_df[filtered_df['energy_100g'] <= energy_threshold]
        
        st.info(f"📊 Showing {len(filtered_df):,} products (filtered from {len(df):,})")
        
        # Display data
        display_cols = ['product_name', 'brands', 'countries', 'energy_100g', 
                       'sugars_100g', 'fat_100g', 'proteins_100g']
        display_cols = [col for col in display_cols if col in filtered_df.columns]
        
        st.dataframe(
            filtered_df[display_cols].head(100),
            use_container_width=True,
            height=500
        )
        
        # Download option
        csv = filtered_df[display_cols].to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name="filtered_food_data.csv",
            mime="text/csv"
        )

def show_insights():
    """Show insights and recommendations page"""
    st.header("💡 Key Insights & Recommendations")
    st.markdown("Data-driven findings and health recommendations")
    st.markdown("---")
    
    # Key Insights
    st.subheader("🎯 Key Insights Discovered")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 Geographic Patterns
        - **United States** has the highest number of food products in the dataset
        - **US products** tend to have higher sugar and energy content compared to European products
        - **European countries** (France, Switzerland) show more balanced nutritional profiles
        - Regional differences suggest varying food regulations and consumer preferences
        """)
        
        st.markdown("""
        ### 🍬 Sugar Content Analysis
        - Products with **>50g sugar per 100g** are high-risk for diabetes
        - Certain product categories (candies, sodas) consistently show dangerous sugar levels
        - Average sugar content varies significantly by country (up to 40% difference)
        """)
    
    with col2:
        st.markdown("""
        ### 🥓 Fat & Energy Patterns
        - **High-fat products** (>20g per 100g) contribute to cardiovascular diseases
        - **High-calorie products** (>500 kcal per 100g) require portion control
        - Processed snacks and fast food show consistently high fat and energy content
        """)
        
        st.markdown("""
        ### 📈 Data Quality Observations
        - **99.8%** of products have valid names
        - **89.4%** of products have complete nutritional data
        - Data preprocessing successfully cleaned **166,288 records**
        """)
    
    st.markdown("---")
    
    # Recommendations
    st.subheader("⚠️ Health Recommendations")
    
    tab1, tab2, tab3 = st.tabs(["👥 For Consumers", "🏥 For Health Professionals", "🏛️ For Policy Makers"])
    
    with tab1:
        st.markdown("""
        ### 🛒 Smart Shopping Guidelines
        
        **Avoid Products With:**
        - Sugar > 15g per 100g
        - Fat > 20g per 100g
        - Energy > 400 kcal per 100g
        - Long ingredient lists with additives
        
        **Prefer Products With:**
        - Natural ingredients
        - Lower sugar and fat content
        - Higher protein and fiber content
        - Clear nutritional labeling
        
        **Tips:**
        - Compare similar products from different brands
        - Check serving sizes carefully
        - Look for products from regions with healthier profiles
        - Use this dashboard to make informed decisions
        """)
    
    with tab2:
        st.markdown("""
        ### 👨‍⚕️ Clinical Guidelines
        
        **For Diet Planning:**
        - Use country-specific data to recommend regional alternatives
        - Identify high-risk products to avoid for specific conditions
        - Create meal plans based on data-driven nutritional profiles
        
        **For Patient Education:**
        - Show evidence of unhealthy products using this dashboard
        - Explain geographic variations in food quality
        - Demonstrate impact of product choices on health
        
        **For Research:**
        - Analyze correlations between food consumption and health outcomes
        - Track temporal trends in nutritional content
        - Compare effectiveness of different dietary interventions
        """)
    
    with tab3:
        st.markdown("""
        ### 🏛️ Policy Recommendations
        
        **Regulatory Actions:**
        - Implement **sugar tax** on products with >20g sugar per 100g
        - Mandate **clear labeling** of high-risk nutritional content
        - Restrict **marketing** of unhealthy products to children
        - Set **maximum limits** for sugar, fat, and additives
        
        **Public Health Campaigns:**
        - Focus on high-sugar product categories (sodas, candies)
        - Target regions with unhealthy food consumption patterns
        - Educate consumers using data-driven insights
        
        **Industry Collaboration:**
        - Encourage reformulation of high-risk products
        - Incentivize production of healthier alternatives
        - Support transparency in nutritional information
        """)
    
    st.markdown("---")
    
    # Future Enhancements
    st.subheader("🚀 Future Enhancements")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🤖 Machine Learning**
        - Health risk prediction models
        - Product recommendation system
        - Dietary pattern analysis
        """)
    
    with col2:
        st.markdown("""
        **📱 Mobile App**
        - Barcode scanning
        - Real-time product lookup
        - Personalized recommendations
        """)
    
    with col3:
        st.markdown("""
        **🔄 Real-time Updates**
        - Live data feeds from APIs
        - Automated data refresh
        - Trend monitoring
        """)

if __name__ == "__main__":
    main()
