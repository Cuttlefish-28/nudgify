import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re  # ✅ Regular expressions for SMS parsing
from streamlit_lottie import st_lottie
import requests
from streamlit_option_menu import option_menu

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Nudgify", layout="wide")

# ------------------ CUSTOM STYLING ------------------
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #fce4ec, #e1f5fe);
    }
    .card {
        background-color: #fff9c4;
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin: 0.5rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ LOAD LOTTIE ANIMATIONS ------------------
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

nudgy_lottie = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_i2eyukor.json")

# ------------------ SIDEBAR NAV ------------------
with st.sidebar:
    selected = option_menu(
        menu_title="Nudgify",
        options=["Home", "About"],
        icons=["house", "info-circle"],
        menu_icon="wallet",
        default_index=0,
    )

# ------------------ HOME PAGE ------------------
if selected == "Home":
    col1, col2 = st.columns([1, 2])
    with col1:
        st_lottie(nudgy_lottie, height=250, key="nudgy")
    with col2:
        st.title("💸 Nudgify")
        st.markdown("Your Smart Spending Buddy for young souls. 💖")

    tab1, tab2, tab3 = st.tabs(["📂 Upload", "📊 Insights", "💡 Nudges"])

    with tab1:
        uploaded_file = st.file_uploader("Upload your transaction CSV", type="csv")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.success("✅ File uploaded successfully!")

            if 'Merchant' in df.columns and 'Category' not in df.columns:
                merchant_to_category = {
                    'Zomato': 'Food', 'Swiggy': 'Food', 'Dominos': 'Food',
                    'Amazon': 'Shopping', 'Flipkart': 'Shopping', 'Nykaa': 'Beauty',
                    'Uber': 'Transport', 'Rapido': 'Transport',
                    'H&M': 'Clothing', 'Myntra': 'Clothing'
                }
                df['Merchant'] = df['Merchant'].str.strip().str.title()
                df['Category'] = df['Merchant'].map(lambda x: merchant_to_category.get(x, 'Others'))
            st.dataframe(df.head())

    with tab2:
        if uploaded_file and 'Amount' in df.columns:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            df.dropna(subset=['Amount'], inplace=True)

            if 'Category' not in df.columns and 'Merchant' in df.columns:
                merchant_to_category = {
                    'Swiggy': 'Food', 'Zomato': 'Food', 'Dominos': 'Food',
                    'Amazon': 'Shopping', 'Flipkart': 'Shopping', 'Nykaa': 'Beauty',
                    'Uber': 'Transport', 'Rapido': 'Transport',
                    'H&M': 'Clothing', 'Myntra': 'Clothing'
                }
                df['Merchant'] = df['Merchant'].str.strip().str.title()
                df['Category'] = df['Merchant'].map(lambda x: merchant_to_category.get(x, 'Others'))

            if 'Category' in df.columns:
                st.subheader("📍 Category Breakdown")
                category_spend = df.groupby('Category')['Amount'].sum()
                fig, ax = plt.subplots()
                category_spend.plot(kind='pie', autopct='%1.1f%%', ax=ax)
                ax.set_ylabel("")
                st.pyplot(fig)

                st.subheader("📈 Budget Usage")
                user_budget_insight = st.number_input("Enter your monthly budget (₹):", min_value=0, value=15000, step=500, key="budget_tab2")

                total_spent = df['Amount'].sum()
                if user_budget_insight > 0:
                    percent_spent = (total_spent / user_budget_insight) * 100

                    fig2, ax2 = plt.subplots(figsize=(4, 4))
                    wedges, _ = ax2.pie([percent_spent, 100 - percent_spent],
                                        startangle=90, counterclock=False,
                                        colors=['#4CAF50', '#E0E0E0'],
                                        wedgeprops=dict(width=0.3))
                    ax2.text(0, 0, f"{percent_spent:.1f}%", ha='center', va='center', fontsize=16, fontweight='bold')
                    ax2.set(aspect="equal")
                    st.pyplot(fig2)

                    if percent_spent >= 100:
                        st.error("🚨 You've spent 100% or more of your budget!")
                    elif percent_spent >= 80:
                        st.warning(f"⚠️ {percent_spent:.1f}% of your budget is already used.")
                    else:
                        st.success(f"💚 Only {percent_spent:.1f}% of your budget spent — keep going smart!")
                else:
                    st.warning("Please enter a valid monthly budget.")
            else:
                st.warning("🟨 No 'Category' column found for pie chart.")

    with tab3:
        if uploaded_file and 'Amount' in df.columns:
            avg_spend = df['Amount'].mean()
            total_spend = df['Amount'].sum()

            st.subheader("✨ Your Nudgify Suggestions")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("#### 💰 Total Spend")
                st.markdown(f"<div class='card'>₹ {total_spend:.2f}</div>", unsafe_allow_html=True)

            with col2:
                st.markdown("#### 📉 Average Spend")
                st.markdown(f"<div class='card'>₹ {avg_spend:.2f}</div>", unsafe_allow_html=True)

            with col3:
                st.markdown("#### 🎯 Monthly Target")
                monthly_target = 15000
                st.markdown(f"<div class='card'>₹ {monthly_target:.2f}</div>", unsafe_allow_html=True)

            st.markdown("### 👀 Nudgify Says:")
            if total_spend > 25000:
                st.error("🔥 Big spender alert! Swap food delivery for home-cooked magic ✨")
            if avg_spend > 1000:
                st.info("🤑 High roller vibes! Consider reviewing subscriptions & auto-pays.")
            if 'Swiggy' in df.get('Merchant', []).values:
                st.warning("🍟 Frequent Swiggy orders detected. Challenge: No Swiggy Sundays!")
            if 'Amazon' in df.get('Merchant', []).values:
                st.info("📦 Amazon splurge? Wishlist items for 3 days before buying.")
            if total_spend < 10000:
                st.success("💚 You're crushing it! Maybe invest in an index fund next?")

# ------------------ ABOUT PAGE ------------------
if selected == "About":
    st.title("👩‍💻 About Nudgify")
    st.markdown("""
    Nudgify is your Gen Z friendly personal spending advisor 🧠💸.
    It reads your expenses, finds patterns, and gives cheeky yet helpful nudges to keep you on track.

    Made with ❤️ using Python, Streamlit, Matplotlib, Pandas and some hard work.
    """)

