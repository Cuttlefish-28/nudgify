import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_lottie import st_lottie
import requests

# 🎨 Set Streamlit config and custom background
st.set_page_config(page_title="Nudgify", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #fce4ec, #e0f7fa);
        color: #333;
    }
    .card {
        background-color: #fff9c4;
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# 🔄 Load Lottie animation
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

nudgy_lottie = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_i2eyukor.json")

# 🔝 Header with animation
col1, col2 = st.columns([1, 2])
with col1:
    st_lottie(nudgy_lottie, height=250, key="nudgy")
with col2:
    st.title("💸 Nudgify")
    st.markdown("Your Smart Spending Buddy for Gen Z 💖\nGet stylish nudges that help you save better, live smarter.")

# 📍 Tabs
tab1, tab2, tab3 = st.tabs(["📂 Upload CSV", "📈 Breakdown", "💡 Nudges"])

with tab1:
    uploaded_file = st.file_uploader("Upload your transaction CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success("✅ File uploaded successfully!")
        st.write(df.head())

with tab2:
    if uploaded_file and 'Amount' in df.columns:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        df.dropna(subset=['Amount'], inplace=True)

        if 'Category' in df.columns:
            st.subheader("🧁 Category Breakdown")
            category_spend = df.groupby('Category')['Amount'].sum()
            fig, ax = plt.subplots()
            category_spend.plot(kind='pie', autopct='%1.1f%%', ax=ax)
            ax.set_ylabel("")
            st.pyplot(fig)
        else:
            st.warning("🟨 No 'Category' column found for pie chart.")
    elif uploaded_file:
        st.error("🔴 'Amount' column is missing or invalid!")

with tab3:
    if uploaded_file and 'Amount' in df.columns:
        avg_spend = df['Amount'].mean()
        total_spend = df['Amount'].sum()

        st.subheader("✨ Your Nudgify Suggestions")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 🔍 Total Spend")
            st.markdown(f"<div class='card'>₹ {total_spend:.2f}</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("#### 📉 Average Spend")
            st.markdown(f"<div class='card'>₹ {avg_spend:.2f}</div>", unsafe_allow_html=True)

        with col3:
            st.markdown("#### 📅 Monthly Target")
            monthly_target = 15000
            st.markdown(f"<div class='card'>₹ {monthly_target:.2f}</div>", unsafe_allow_html=True)

        # 💡 Nudges
        st.markdown("### 👀 Nudgify Says:")

        if total_spend > 20000:
            st.success("🚨 **You're on a spending spree!** Maybe skip Swiggy for a week?")
        elif avg_spend > 500:
            st.info("🛍️ You're vibing premium! Consider a budgeting app or review auto-debits.")
        else:
            st.balloons()
            st.success("💚 Smart spender spotted! Ever thought of investing the extra ₹₹₹?")
