import streamlit as st
import pandas as pd
import os

# --- Page Setup ---
st.set_page_config(
    page_title="Multi-Platform Orders Dashboard",
    page_icon="🛒",
    layout="wide"
)

# --- Clean Card Styling ---
st.markdown("""
<style>
    .order-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .badge-cat {
        background-color: #fee2e2;
        color: #b91c1c;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-status {
        background-color: #dcfce7;
        color: #15803d;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: 600;
    }
    .order-id-tag {
        color: #64748b;
        font-size: 11px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.title("🛒 Multi-Platform Orders Archive & Insights")
st.caption("Search, review past purchases, and track ordering trends across Amazon, Flipkart, Myntra, and more.")

# --- File Loader & Column Normalizer ---
uploaded_file = st.file_uploader("Upload your orders file (CSV or Excel)", type=["csv", "xlsx"])


def load_dataset():
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        return pd.read_excel(uploaded_file)
    elif os.path.exists("Sales.csv"):
        # Auto-loads local Sales.csv if present in the same folder
        return pd.read_csv("Sales.csv")
    return None


def standardize_columns(df):
    cols = {str(col).lower().strip(): col for col in df.columns}

    # Matches standard field names across Amazon, Flipkart, and generic sales reports
    field_map = {
        'title': ['item title', 'title', 'product name', 'description', 'product title', 'item name', 'product'],
        'price': ['item subtotal', 'total amount', 'price', 'item price', 'selling price', 'sales', 'order amount'],
        'order_id': ['order id', 'order_id', 'order id / sub order id', 'order number'],
        'date': ['order date', 'date', 'placed date', 'ship date'],
        'category': ['category', 'department', 'product vertical', 'sub-category'],
        'status': ['shipment status', 'order status', 'status', 'delivery status'],
        'qty': ['quantity', 'qty', 'units']
    }

    cleaned = pd.DataFrame()
    for std_col, candidates in field_map.items():
        matched = next((cols[c] for c in candidates if c in cols), None)
        if matched:
            cleaned[std_col] = df[matched]
        else:
            cleaned[std_col] = "N/A"

    # Data transformations
    cleaned['price'] = (
        cleaned['price']
        .astype(str)
        .str.replace(r'[^\d.]', '', regex=True)
    )
    cleaned['price'] = pd.to_numeric(cleaned['price'], errors='coerce').fillna(0.0)
    cleaned['qty'] = pd.to_numeric(cleaned['qty'], errors='coerce').fillna(1).astype(int)
    cleaned['date'] = pd.to_datetime(cleaned['date'], errors='coerce')
    cleaned['category'] = cleaned['category'].replace('N/A', 'General').fillna('General')
    cleaned['status'] = cleaned['status'].replace('N/A', 'Completed').fillna('Completed')

    return cleaned


raw_df = load_dataset()

if raw_df is not None:
    df = standardize_columns(raw_df)

    # --- Top KPI Summary Cards ---
    total_spend = df['price'].sum()
    total_orders = df['order_id'].nunique() if (df['order_id'] != "N/A").any() else len(df)
    avg_order = (total_spend / total_orders) if total_orders > 0 else 0
    top_cat = df['category'].value_counts().index[0] if not df['category'].empty else "N/A"

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("TOTAL SPEND", f"₹{total_spend:,.2f}")
    k2.metric("TOTAL ORDERS", f"{total_orders:,}")
    k3.metric("AVERAGE ORDER VALUE", f"₹{avg_order:,.2f}")
    k4.metric("TOP DEPARTMENT", str(top_cat))

    st.markdown("---")

    # --- Search & Filter Bar ---
    search_query = st.text_input("🔍 Search orders by item name, order ID, or category...")

    f1, f2, f3 = st.columns(3)
    valid_years = sorted(df['date'].dt.year.dropna().unique().astype(int).tolist(), reverse=True)
    year_options = ['All'] + valid_years
    selected_year = f1.selectbox("Filter by Year", year_options)

    cat_options = ['All'] + sorted(df['category'].dropna().unique().tolist())
    selected_cat = f2.selectbox("Filter by Category", cat_options)

    sort_order = f3.selectbox(
        "Sort By",
        ["Newest First", "Oldest First", "Price: High to Low", "Price: Low to High"]
    )

    # Apply Filters
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df['title'].astype(str).str.contains(search_query, case=False, na=False) |
            filtered_df['order_id'].astype(str).str.contains(search_query, case=False, na=False) |
            filtered_df['category'].astype(str).str.contains(search_query, case=False, na=False)
            ]

    if selected_year != 'All':
        filtered_df = filtered_df[filtered_df['date'].dt.year == selected_year]

    if selected_cat != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_cat]

    # Apply Sorting
    if sort_order == "Newest First":
        filtered_df = filtered_df.sort_values(by='date', ascending=False)
    elif sort_order == "Oldest First":
        filtered_df = filtered_df.sort_values(by='date', ascending=True)
    elif sort_order == "Price: High to Low":
        filtered_df = filtered_df.sort_values(by='price', ascending=False)
    elif sort_order == "Price: Low to High":
        filtered_df = filtered_df.sort_values(by='price', ascending=True)

    st.write(f"Showing **{len(filtered_df)}** records")

    # --- 3-Column Card Layout ---
    cols_per_row = 3
    for i in range(0, len(filtered_df), cols_per_row):
        row_slice = filtered_df.iloc[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        for idx, (_, item) in enumerate(row_slice.iterrows()):
            with cols[idx]:
                date_str = item['date'].strftime('%d %b %Y') if pd.notnull(item['date']) else 'Recent'
                title_display = str(item['title'])
                if len(title_display) > 70:
                    title_display = title_display[:70] + "..."

                st.markdown(f"""
                <div class="order-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 12px; color: #64748b;">📅 {date_str}</span>
                        <strong style="color: #0f172a; font-size: 15px;">₹{item['price']:,.2f}</strong>
                    </div>
                    <div style="margin-bottom: 8px;">
                        <span class="order-id-tag">ID: {item['order_id']}</span> &nbsp;
                        <span class="badge-cat">{item['category']}</span>
                    </div>
                    <div style="font-size: 13px; font-weight: 600; color: #1e293b; min-height: 38px; margin-bottom: 10px;">
                        {title_display}
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #64748b;">
                        <span>Qty: {item['qty']}</span>
                        <span class="badge-status">{item['status']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.info("👆 Please upload an order report (CSV or Excel) to see your metrics and card layout.")

