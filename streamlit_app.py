"""
Streamlit Dashboard for Used Car Price Prediction API
Dynamically consumes all 5 FastAPI endpoints
"""

import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime

# ─── Page Config ───
st.set_page_config(
    page_title="Used Car Analytics",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS Styling ───
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1f77b4; }
    .sub-header { font-size: 1.2rem; color: #666; margin-bottom: 2rem; }
    .metric-card { background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #1f77b4; }
    .error-box { background: #ffebee; padding: 1rem; border-radius: 8px; border-left: 4px solid #d32f2f; }
    .success-box { background: #e8f5e9; padding: 1rem; border-radius: 8px; border-left: 4px solid #388e3c; }
    .stDataFrame { font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ───
st.sidebar.markdown("## ⚙️ API Configuration")
API_BASE = st.sidebar.text_input("API Base URL", "http://localhost:8000")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Navigation")
page = st.sidebar.radio(
    "Go to",
    ["🏠 Home", "🔍 Data Explorer", "🚗 Car Lookup", "📈 Data Quality", "📊 Summary Stats", "🔬 Column Profiler"]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Backend must be running:**
```bash
uvicorn src.main:app --reload --port 8000
                """)

@st.cache_data(ttl=30)
def fetch_cars(page=1, page_size=50, **filters):
    """Endpoint 1: GET /cars/"""
    params = {"page": page, "page_size": page_size}
    params.update({k: v for k, v in filters.items() if v})
    try:
        resp = requests.get(f"{API_BASE}/cars/", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}
    
@st.cache_data(ttl=60)
def fetch_car_by_id(car_id):
    """Endpoint 2: GET /cars/{car_id}"""
    try:
        resp = requests.get(f"{API_BASE}/cars/{car_id}", timeout=10)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=60)
def fetch_summary_stats():
    """Endpoint 3: GET /cars/stats/summary"""
    try:
        resp = requests.get(f"{API_BASE}/cars/stats/summary", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=60)
def fetch_quality_report():
    """Endpoint 4: GET /cars/stats/quality"""
    try:
        resp = requests.get(f"{API_BASE}/cars/stats/quality", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

@st.cache_data(ttl=60)
def fetch_unique_values(column):
    """Endpoint 5: GET /cars/columns/{column}/unique"""
    try:
        resp = requests.get(f"{API_BASE}/cars/columns/{column}/unique", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def check_api_health():
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=5)
        return resp.status_code == 200
    except:
        return False
    
if page == "🏠 Home":
    st.markdown('<p class="main-header">', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("API Status", "🟢 Online" if check_api_health() else "🔴 Offline")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        try:
            health = requests.get(f"{API_BASE}/health", timeout=5).json()
            st.metric("Data Loaded", "✅ Yes" if health.get("data_loaded") else "❌ No")
        except:
            st.metric("Data Loaded", "❌ Unknown")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        try:
            root = requests.get(f"{API_BASE}/", timeout=5).json()
            st.metric("Total Cars", f"{root.get('total_cars', 0):,}")
        except:
            st.metric("Total Cars", "N/A")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📡 Available Endpoints")

    endpoints = {
        "GET /cars/": "List all cars with pagination & filtering",
        "GET /cars/{id}": "Get single car details",
        "GET /cars/stats/summary": "Summary statistics (price, mileage, year)",
        "GET /cars/stats/quality": "Data quality report (messiness metrics)",
        "GET /cars/columns/{col}/unique": "Unique values per column"
    }

    for endpoint, desc in endpoints.items():
        st.markdown(f"**`{endpoint}`** — {desc}")

    st.markdown("---")
    st.markdown("### 🚀 Quick Start")
    st.code("""
    uvicorn src.main:app --reload --port 8000
    streamlit run streamlit_app.py
    """, language="bash")

elif page == "🔍 Data Explorer":
    st.markdown('<p class="main-header">', unsafe_allow_html=True)
    st.markdown("Browse the raw messy dataset with live filtering.")

    # Filters
    with st.expander("🔧 Filters", expanded=True):
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            make_filter = st.text_input("Make", placeholder="e.g., Toyota")
            min_year = st.number_input("Min Year", 1990, 2025, 1990)
        with fcol2:
            model_filter = st.text_input("Model", placeholder="e.g., Camry")
            max_year = st.number_input("Max Year", 1990, 2025, 2025)
        with fcol3:
            fuel_filter = st.text_input("Fuel Type", placeholder="e.g., Gasoline")
            page_size = st.selectbox("Records per page", [10, 25, 50, 100], index=2)

    # Pagination
    page_num = st.number_input("Page", min_value=1, value=1, step=1)

    # Fetch data
    with st.spinner("Fetching data from API..."):
        data = fetch_cars(
            page=page_num,
            page_size=page_size,
            make=make_filter or None,
            model=model_filter or None,
            fuel_type=fuel_filter or None,
            min_year=min_year,
            max_year=max_year
        )

    if "error" in data:
        st.error(f"❌ API Error: {data['error']}")
    else:
        st.success(f"✅ Found **{data['total_records']:,}** records | Showing page **{data['page']}** of **{(data['total_records'] // page_size) + 1}**")

        df = pd.DataFrame(data["data"])
        if not df.empty:
            st.dataframe(df, width="stretch", height=500)
        
            # Download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Current Page as CSV",
                csv,
                f"cars_page_{page_num}.csv",
                "text/csv"
            )
        else:
            st.warning("No records match your filters.")

elif page == "🚗 Car Lookup":
    st.markdown('<p class="main-header">', unsafe_allow_html=True)
    st.markdown("Search for a specific car by its ID.")
    car_id = st.text_input("Enter Car ID", placeholder="e.g., CAR-923820")

    if st.button("🔍 Search", type="primary"):
        if car_id:
            with st.spinner("Fetching car details..."):
                car = fetch_car_by_id(car_id)

            if car is None:
                st.error(f"❌ Car `{car_id}` not found.")
            elif "error" in car:
                st.error(f"❌ Error: {car['error']}")
            else:
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.markdown(f"### ✅ Found: {car.get('car_id')}")
                st.markdown('</div>', unsafe_allow_html=True)

                # Display as cards
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📋 Basic Info")
                    st.markdown(f"**Make:** `{car.get('make')}`")
                    st.markdown(f"**Model:** `{car.get('model')}`")
                    st.markdown(f"**Year:** `{car.get('year')}`")
                    st.markdown(f"**Mileage:** `{car.get('mileage')}`")
                    st.markdown(f"**Color:** `{car.get('color')}`")
                    st.markdown(f"**Body Type:** `{car.get('body_type')}`")
                    st.markdown(f"**Condition:** `{car.get('condition')}`")
                
                with col2:
                    st.markdown("#### 💰 Pricing & Details")
                    st.markdown(f"**Listing Price:** `{car.get('listing_price')}`")
                    st.markdown(f"**Fuel Type:** `{car.get('fuel_type')}`")
                    st.markdown(f"**Transmission:** `{car.get('transmission')}`")
                    st.markdown(f"**Engine:** `{car.get('engine_size')}`")
                    st.markdown(f"**Horsepower:** `{car.get('horsepower')}`")
                    st.markdown(f"**Owners:** `{car.get('owners')}`")
                    st.markdown(f"**Title Status:** `{car.get('title_status')}`")

                st.markdown("---")
                st.markdown("#### 📍 Location & Listing")
                st.markdown(f"**City:** `{car.get('city')}` | **State:** `{car.get('registration_state')}` | **ZIP:** `{car.get('zip_code')}`")
                st.markdown(f"**Listing Date:** `{car.get('listing_date')}` | **Days on Market:** `{car.get('days_on_market')}`")
                st.markdown(f"**Seller Type:** `{car.get('seller_type')}`")

                st.markdown("---")
                st.markdown("#### 🛠️ Features")
                feat_col1, feat_col2, feat_col3 = st.columns(3)
                with feat_col1:
                    st.markdown(f"Navigation: `{car.get('has_navigation')}`")
                    st.markdown(f"Bluetooth: `{car.get('has_bluetooth')}`")
                with feat_col2:
                    st.markdown(f"Backup Camera: `{car.get('has_backup_camera')}`")
                    st.markdown(f"Sunroof: `{car.get('has_sunroof')}`")
                with feat_col3:
                    st.markdown(f"Leather Seats: `{car.get('has_leather_seats')}`")
                    st.markdown(f"Heated Seats: `{car.get('has_heated_seats')}`")

                # Raw JSON
                with st.expander("📝 Raw JSON Response"):
                    st.json(car)
        else:
            st.warning("Please enter a Car ID.")

elif page == "📈 Data Quality":
    st.markdown('<p class="main-header">', unsafe_allow_html=True)
    st.markdown("Understand the messiness before cleaning.")
    with st.spinner("Fetching quality report from API..."):
        report = fetch_quality_report()

    if "error" in report:
        st.error(f"❌ API Error: {report['error']}")
    else:
        # Top metrics
        qcol1, qcol2, qcol3, qcol4 = st.columns(4)
        with qcol1:
            st.metric("Total Rows", f"{report['total_rows']:,}")
        with qcol2:
            st.metric("Total Columns", report['total_columns'])
        with qcol3:
            st.metric("Duplicate Rows", f"{report['duplicate_rows']:,}")
        with qcol4:
            missing_total = sum(report['missing_values'].values())
            st.metric("Total Missing", f"{missing_total:,}")

        st.markdown("---")

        # Issue cards
        st.markdown("### 🚨 Data Quality Issues")
        icol1, icol2, icol3, icol4 = st.columns(4)
        with icol1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f"**Negative Prices:** `{report['negative_prices']:,}`")
            st.markdown('</div>', unsafe_allow_html=True)
        with icol2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f"**Negative Mileage:** `{report['negative_mileage']:,}`")
            st.markdown('</div>', unsafe_allow_html=True)
        with icol3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f"**Invalid Years:** `{report['invalid_years']:,}`")
            st.markdown('</div>', unsafe_allow_html=True)
        with icol4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f"**Price Outliers (>$200k):** `{report['price_outliers']:,}`")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Missing values chart
        st.markdown("### 📊 Missing Values by Column")
        missing_df = pd.DataFrame({
            "Column": list(report['missing_values'].keys()),
            "Missing Count": list(report['missing_values'].values())
        }).sort_values("Missing Count", ascending=False)

        st.bar_chart(missing_df.set_index("Column"))

        # Data types table
        st.markdown("### 🏷️ Data Types (Raw)")
        dtype_df = pd.DataFrame({
            "Column": list(report['data_types'].keys()),
            "Pandas Dtype": list(report['data_types'].values())
        })
        st.dataframe(dtype_df, width="stretch")

        # Sample records
        st.markdown("### 🧪 Sample Raw Records")
        sample_df = pd.DataFrame(report['sample_records'])
        st.dataframe(sample_df, width="stretch")

elif page == "📊 Summary Stats":
    st.markdown('<p class="main-header">', unsafe_allow_html=True)
    st.markdown("Numeric insights from the raw dataset.")
    with st.spinner("Fetching summary stats from API..."):
        stats = fetch_summary_stats()

    if "error" in stats:
        st.error(f"❌ API Error: {stats['error']}")
    else:
        # Price stats
        st.markdown("### 💰 Price Statistics")
        if stats.get("price_stats"):
            p = stats["price_stats"]
            pcol1, pcol2, pcol3, pcol4, pcol5 = st.columns(5)
            with pcol1:
                st.metric("Count", f"{p.get('count', 0):,}")
            with pcol2:
                st.metric("Mean", f"${p.get('mean', 0):,.2f}")
            with pcol3:
                st.metric("Median", f"${p.get('median', 0):,.2f}")
            with pcol4:
                st.metric("Min", f"${p.get('min', 0):,.2f}")
            with pcol5:
                st.metric("Max", f"${p.get('max', 0):,.2f}")

        # Mileage stats
        st.markdown("### 🛣️ Mileage Statistics")
        if stats.get("mileage_stats"):
            m = stats["mileage_stats"]
            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
            with mcol1:
                st.metric("Count", f"{m.get('count', 0):,}")
            with mcol2:
                st.metric("Mean", f"{m.get('mean', 0):,.0f}")
            with mcol3:
                st.metric("Min", f"{m.get('min', 0):,.0f}")
            with mcol4:
                st.metric("Max", f"{m.get('max', 0):,.0f}")

        # Year stats
        st.markdown("### 📅 Year Statistics")
        if stats.get("year_stats"):
            y = stats["year_stats"]
            ycol1, ycol2, ycol3 = st.columns(3)
            with ycol1:
                st.metric("Count", f"{y.get('count', 0):,}")
            with ycol2:
                st.metric("Min Year", y.get('min', 'N/A'))
            with ycol3:
                st.metric("Max Year", y.get('max', 'N/A'))

        st.markdown("---")

        # Categorical distributions
        st.markdown("### 🏭 Make Distribution (Top 10)")
        if stats.get("make_distribution"):
            make_df = pd.DataFrame({
                "Make": list(stats["make_distribution"].keys()),
                "Count": list(stats["make_distribution"].values())
            }).sort_values("Count", ascending=False)
            st.bar_chart(make_df.set_index("Make"))

        st.markdown("### ⛽ Fuel Type Distribution")
        if stats.get("fuel_type_distribution"):
            fuel_df = pd.DataFrame({
                "Fuel Type": list(stats["fuel_type_distribution"].keys()),
                "Count": list(stats["fuel_type_distribution"].values())
            }).sort_values("Count", ascending=False)
            st.bar_chart(fuel_df.set_index("Fuel Type"))

        st.markdown("### 🔧 Condition Distribution")
        if stats.get("condition_distribution"):
            cond_df = pd.DataFrame({
                "Condition": list(stats["condition_distribution"].keys()),
                "Count": list(stats["condition_distribution"].values())
            }).sort_values("Count", ascending=False)
            st.bar_chart(cond_df.set_index("Condition"))

elif page == "🔬 Column Profiler":
    st.markdown('<p class="main-header">', unsafe_allow_html=True)
    st.markdown("Inspect unique values in any column to spot inconsistencies and typos.")
    columns = [
        "make", "model", "fuel_type", "transmission", "color", 
        "body_type", "condition", "title_status", "seller_type", 
        "registration_state", "accident_history", "service_history"
    ]

    selected_col = st.selectbox("Select a column to profile", columns)

    if st.button("🔍 Fetch Unique Values", type="primary"):
        with st.spinner(f"Fetching unique values for `{selected_col}`..."):
            result = fetch_unique_values(selected_col)

        if "error" in result:
            st.error(f"❌ API Error: {result['error']}")
        else:
            st.success(f"✅ Found **{result['unique_count']}** unique values in `{result['column']}`")

            # Show as dataframe
            values_df = pd.DataFrame({
                "Value": result["values"]
            })
            st.dataframe(values_df, width="stretch", height=400)

            # Highlight potential issues
            st.markdown("### 🚨 Potential Issues Detected")
            issues = []
            for val in result["values"]:
                if pd.isna(val) or str(val).strip() == "":
                    issues.append(f"Empty/Null value")
                elif str(val).strip() != str(val):
                    issues.append(f"Whitespace issue: `{repr(val)}`")
                elif str(val).islower() or str(val).isupper():
                    if len(str(val)) > 1:
                        issues.append(f"Inconsistent case: `{val}`")
            
            # Check for typos in make
            if selected_col == "make":
                known_typos = ["Toyata", "Hnda", "BWM", "Merc", "Audii", "Lexs", "Nisan", "Hyuandai", "Kiaa", "Volkswagon"]
                for val in result["values"]:
                    if str(val) in known_typos:
                        issues.append(f"Known typo: `{val}`")

            if issues:
                for issue in set(issues):
                    st.warning(issue)
            else:
                st.info("No obvious issues detected in this column.")

            # Raw JSON
            with st.expander("📝 Raw JSON Response"):
                st.json(result)