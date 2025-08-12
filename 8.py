import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="GST-Based Dynamic Pricing Simulator", page_icon="💰", layout="centered")

st.title("GST-Based Dynamic Pricing Simulator")
st.subheader("Adjust business factors and get smart pricing suggestions")

# Session state for history
if "history" not in st.session_state:
    st.session_state.history = []

# GST Categories
gst_rates = {
    "Essentials": 0.00,
    "Food Items": 0.05,
    "Apparel under ₹1,000": 0.05,
    "Apparel above ₹1,000": 0.12,
    "Electronics": 0.18,
    "Luxury Goods": 0.28
}

# Sidebar inputs
st.sidebar.header("Pricing Inputs")
product_name = st.sidebar.text_input("Product Name", placeholder="Enter product name")
category = st.sidebar.selectbox("GST Category", list(gst_rates.keys()))
competitor_price = st.sidebar.number_input("Competitor Price (₹)", min_value=1.0, value=100.0, step=1.0)

# Quick Toggles
st.sidebar.subheader("Quick Scenarios")
scenario = st.sidebar.radio(
    "Choose Scenario",
    ("Custom", "High Demand, Low Stock", "Clearance Sale", "Festive Boost")
)

if scenario == "High Demand, Low Stock":
    demand, stock, seasonal, discount = 90, 20, False, 0
elif scenario == "Clearance Sale":
    demand, stock, seasonal, discount = 40, 80, False, 30
elif scenario == "Festive Boost":
    demand, stock, seasonal, discount = 70, 50, True, 10
else:
    demand = st.sidebar.slider("Demand (%)", 0, 100, 50)
    stock = st.sidebar.slider("Stock Availability (%)", 0, 100, 50)
    seasonal = st.sidebar.checkbox("Apply Seasonal Increase (10%)")
    discount = st.sidebar.slider("Discount (%)", 0, 50, 0)

cost_price = st.sidebar.number_input("Cost Price (₹)", min_value=0.0, value=50.0, step=1.0)

# Pricing calculation
base_price = competitor_price
demand_factor = 1 + (demand / 100 * 0.2)
stock_factor = 1 - (stock / 100 * 0.15)
seasonal_factor = 1.1 if seasonal else 1
gst_rate = gst_rates[category]

pre_gst_price = base_price * demand_factor * stock_factor * seasonal_factor
discount_amount = pre_gst_price * (discount / 100)
price_after_discount = pre_gst_price - discount_amount
gst_amount = price_after_discount * gst_rate
final_price = price_after_discount + gst_amount
profit = final_price - cost_price
profit_margin = (profit / final_price) * 100 if final_price > 0 else 0

# Save to history
if st.sidebar.button("Save Recommendation"):
    st.session_state.history.append({
        "Product": product_name,
        "Category": category,
        "Final Price": round(final_price, 2),
        "Profit Margin %": round(profit_margin, 2)
    })

# Display results
col1, col2 = st.columns(2)
with col1:
    st.metric("Pre-GST Price", f"₹{pre_gst_price:.2f}")
    st.metric("Discount Applied", f"-₹{discount_amount:.2f} ({discount}%)")
    st.metric("GST Rate", f"{gst_rate*100:.0f}%")
with col2:
    st.metric("Final Price", f"₹{final_price:.2f}")
    st.metric("Profit Margin", f"{profit_margin:.2f}%")

# GST Breakdown Table
st.subheader("GST Breakdown")
breakdown_df = pd.DataFrame({
    "Component": ["Base Price (Pre-Discount)", "Discount", "Price After Discount", "GST Amount", "Final Price"],
    "Amount (₹)": [pre_gst_price, -discount_amount, price_after_discount, gst_amount, final_price]
})
st.table(breakdown_df)

# Enhanced pie chart breakdown
labels = ['Price After Discount', 'Discount', 'GST']
sizes = [price_after_discount, discount_amount, gst_amount]
colors = ['#4CAF50', '#FF9800', '#03A9F4']

fig1, ax1 = plt.subplots()
ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
ax1.axis('equal')
st.pyplot(fig1)

# Bar chart comparison
comparison_data = pd.DataFrame({
    'Price Type': ['Competitor Price', 'Pre-GST Price', 'Final Price'],
    'Price': [competitor_price, pre_gst_price, final_price]
})
fig2, ax2 = plt.subplots()
ax2.bar(comparison_data['Price Type'], comparison_data['Price'], color=['#FFC107', '#2196F3', '#4CAF50'])
ax2.set_ylabel("₹ Price")
st.pyplot(fig2)

# History table
if st.session_state.history:
    st.subheader("Price Recommendation History")
    st.dataframe(pd.DataFrame(st.session_state.history))

# Explanation expander
with st.expander("How the price is calculated"):
    st.write("""
    - **Base Price**: Taken from competitor price  
    - **Demand Factor**: Increases price if demand is high  
    - **Stock Factor**: Increases price if stock is low  
    - **Seasonal Factor**: Optional +10% increase  
    - **Discount**: Percentage reduction before GST  
    - **GST**: Applied based on product category  
    - **Profit Margin**: Based on cost price entered  
    """)
