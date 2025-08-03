# Nudgify App - Aesthetic, Gen Z-style Money Nudge App with Analysis & Charts

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit page configuration
st.set_page_config(page_title="\U0001F4B8 Nudgify: Gen Z Money Vibes", layout="centered")

# Custom CSS styling for headings and nudge boxes
st.markdown("""
    <style>
    .big-title {
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        color: #f97316;
    }
    .nudge {
        background-color: #fef3c7;
        border-left: 6px solid #facc15;
        padding: 12px;
        margin: 10px 0;
        border-radius: 10px;
        font-size: 16px;
    }
    .divider {
        border-top: 2px dashed #94a3b8;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="big-title">\U0001F4B3 Nudgify – Track it. Laugh it. Fix it.</div>', unsafe_allow_html=True)

# File uploader
st.markdown("#### Upload your spend file & we'll roast your wallet \U0001F440")
uploaded_file = st.file_uploader("\U0001F4C2 Drop your `.csv` file here (with Merchant & Amount columns)", type=["csv"])

# If file is uploaded
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)  # Load CSV as DataFrame

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.subheader("\U0001F9FE Your Transaction Feed")
    st.dataframe(df, use_container_width=True)  # Show transaction table

    # Basic analysis
    merchant_counts = df["Merchant"].value_counts()  # Count per merchant
    high_spend = df[df["Amount"] > 500]  # Filter high spends

    # Nudge generator logic
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.subheader("\U0001F4A5 Nudgify Says...")
    nudges = []

    # Adding nudges based on logic
    if merchant_counts.get("Swiggy", 0) > 1:
        nudges.append("\U0001F35F Swiggy's got your heart AND your wallet. Time to cook?")
    if merchant_counts.get("Zomato", 0) > 2:
        nudges.append("\U0001F961 Zomato again? You tryna get adopted by them?")
    if "Amazon" in high_spend["Merchant"].values:
        nudges.append("\U0001F6D2 Dropped big bucks on Amazon? Hope it wasn’t another ring light \U0001F605")
    if high_spend["Amount"].max() > 2000:
        nudges.append(f"\U0001F4B8 Biggest spend: ₹{int(high_spend['Amount'].max())}. Rent or regrets?")
    if len(df) > 10 and df["Amount"].mean() > 400:
        nudges.append("\U0001F4C9 Avg spend per item is sus... maybe stop buying dopamine on EMI?")

    # Display nudges or praise
    if nudges:
        for nudge in nudges:
            st.markdown(f'<div class="nudge">👉 {nudge}</div>', unsafe_allow_html=True)
    else:
        st.success("\U0001F44F You’re either broke or super responsible. No nudges today!")

    # Charts section
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.subheader("\U0001F4CA Visualize Your Vibes")

    # Pie chart for merchant distribution
    st.markdown("**\U0001F355 Where your money goes (Top 5 Merchants)**")
    top_merchants = merchant_counts.head(5)
    fig1, ax1 = plt.subplots()
    ax1.pie(top_merchants.values, labels=top_merchants.index, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    st.pyplot(fig1)

    # Bar chart for amount per transaction
    st.markdown("**\U0001F4C8 Spend Trend – Transaction Amounts**")
    fig2, ax2 = plt.subplots()
    df["Amount"].plot(kind='bar', color="#60a5fa", ax=ax2)
    ax2.set_xlabel("Transaction #")
    ax2.set_ylabel("Amount (₹)")
    ax2.set_title("Each Transaction's Cost")
    st.pyplot(fig2)

else:
    st.info("⬆️ Upload a CSV with at least `Merchant` and `Amount` columns to get started.")
