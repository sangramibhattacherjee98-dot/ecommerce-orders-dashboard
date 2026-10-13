# 🛒 Multi-Platform E-Commerce Orders Archive & Analytics Dashboard

An interactive, end-to-end data analytics web application built with Python and Streamlit to standardize, explore, and visualize personal e-commerce purchase history across platforms like Amazon, Flipkart, and Myntra.

🔗 **Live Application:** [View Live App](https://ecommerce-orders-dashboard-mouhrkzru9g58djhk9rs4w.streamlit.app)  
💻 **Source Code:** [GitHub Repository](https://github.com/sangramibhattacherjee98-dot/ecommerce-orders-dashboard)

---

## 📌 Problem Statement
E-commerce platforms export purchase history with conflicting column taxonomies, date conventions, and unstructured item descriptions. Consolidating multi-channel spending usually requires tedious manual spreadsheet manipulation.

## 💡 Solution Architecture
- **Schema Normalization:** An ETL pipeline dynamically reconciles column differences across CSV and XLSX uploads.
- **Dynamic KPI Metrics:** Automatic aggregation of Total Spend, Order Volume, Average Order Value (AOV), and Top Purchasing Category.
- **Interactive Multi-Filter Engine:** Instantaneous filtering across transaction years, product taxonomy, and full-text keyword search across item descriptions.
- **Production Deployment:** Continuous deployment powered by Streamlit Cloud linked to GitHub version control.

---

## 🛠️ Tech Stack
- **Language:** Python
- **Libraries:** Pandas (Data manipulation & cleaning), Openpyxl (Excel parsing)
- **Framework & Deployment:** Streamlit Community Cloud, Git, GitHub

---

## 🚀 Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/sangramibhattacherjee98-dot/ecommerce-orders-dashboard.git](https://github.com/sangramibhattacherjee98-dot/ecommerce-orders-dashboard.git)
   cd ecommerce-orders-dashboard
   pip install -r requirements.txt
   streamlit run main.py
   
