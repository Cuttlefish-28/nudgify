import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
from streamlit_lottie import st_lottie
import requests
from streamlit_option_menu import option_menu
from datetime import datetime

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
        sms_input = st.text_area("Or paste your SMS messages (one per line)", height=200)
        df = None

        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.success("✅ File uploaded successfully!")

        elif sms_input:
            sms_lines = sms_input.strip().split('\n')
            parsed_data = []
            for sms in sms_lines:
                amount_match = re.search(r'(INR|₹|Rs\\.?)?\\s?(\\d+[.,]?\\d*)', sms, re.IGNORECASE)
                amount = float(amount_match.group(2)) if amount_match else None

                merchant_match = re.search(r'(at|for|on|from)\\s+([A-Za-z&]+)', sms, re.IGNORECASE)
                merchant = merchant_match.group(2).title() if merchant_match else "Unknown"

                if "debited" in sms.lower() or "spent" in sms.lower():
                    txn_type = "Debit"
                elif "credited" in sms.lower():
                    txn_type = "Credit"
                else:
                    txn_type = "Unknown"

                date = datetime.today().strftime('%Y-%m-%d')
                parsed_data.append({
                    "Merchant": merchant,
                    "Amount": amount,
                    "Type": txn_type,
                    "Message": sms,
                    "Date": date
                })

            df = pd.DataFrame(parsed_data)
            st.success("✅ SMS parsed successfully!")

        if df is not None:
            df.columns = df.columns.str.strip().str.title()
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
        if df is not None and 'Amount' in df.columns:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            df.dropna(subset=['Amount'], inplace=True)

            st.subheader("📈 Budget Usage")
            user_budget_insight = st.number_input("Enter your monthly budget (₹):", min_value=0, value=15000, step=500, key="budget_tab2")

            total_spent = df['Amount'].sum()
            percent_spent = (total_spent / user_budget_insight * 100) if user_budget_insight > 0 else 0

            if user_budget_insight > 0:
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

            if 'Category' in df.columns:
                st.subheader("📍 Category Breakdown")
                category_spend = df.groupby('Category')['Amount'].sum()
                fig, ax = plt.subplots()
                category_spend.plot(kind='pie', autopct='%1.1f%%', ax=ax)
                ax.set_ylabel("")
                st.pyplot(fig)

    with tab3:
        if df is not None and 'Amount' in df.columns:
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            df.dropna(subset=['Amount'], inplace=True)

            st.subheader("🎯 Set Your Monthly Budget")
            user_budget = st.number_input("Enter your monthly budget (₹):", min_value=0, value=15000, step=500)

            total_spend = df['Amount'].sum()
            avg_spend = df['Amount'].mean()
            avg_daily_budget = user_budget / 30 if user_budget else 0

            today = datetime.today().date()
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                today_spend = df[df['Date'].dt.date == today]['Amount'].sum()
            else:
                today_spend = 0

            st.subheader("📊 Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("#### 💰 Total Spend")
                st.markdown(f"<div class='card'>₹ {total_spend:.2f}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown("#### 📉 Average Spend")
                st.markdown(f"<div class='card'>₹ {avg_spend:.2f}</div>", unsafe_allow_html=True)
            with col3:
                st.markdown("#### 📅 Daily Budget")
                st.markdown(f"<div class='card'>₹ {avg_daily_budget:.2f}</div>", unsafe_allow_html=True)

            st.markdown("### 👀 Nudgify Says:")

            if today_spend > avg_daily_budget:
                st.error(f"⚠️ You've overspent today! ₹{today_spend:.2f} vs your ₹{avg_daily_budget:.0f}/day target.")
            elif today_spend > 0:
                st.info(f"🧠 You're at ₹{today_spend:.2f} today. Stay under ₹{avg_daily_budget:.0f} to be safe.")

            merchant_counts = df['Merchant'].value_counts()
            repeat_merchants = merchant_counts[merchant_counts >= 3].index.tolist()
            for merchant in repeat_merchants:
                if merchant.lower() in ['swiggy', 'zomato']:
                    st.warning(f"🍟 Too much {merchant}? Ordered {merchant_counts[merchant]} times. Explore your kitchen?")
                elif merchant.lower() in ['amazon', 'flipkart', 'nykaa']:
                    st.info(f"🛒 Frequent {merchant} buys? Try 3-day wishlist rule.")

            if total_spend > user_budget:
                st.error("🚨 Over Budget! Time for Maggi nights?")
            elif total_spend > 0.8 * user_budget:
                st.warning("🟨 Almost maxed your budget! Take a pause before spending more.")
            elif total_spend < 0.5 * user_budget:
                st.success("💚 You're doing well! Consider saving or investing the rest.")

# ------------------ ABOUT PAGE ------------------
if selected == "About":
    st.title("👩‍💻 About Nudgify")
    st.markdown("""
    Nudgify is your Gen Z friendly personal spending advisor 🧠💸.
    It reads your expenses, finds patterns, and gives cheeky yet helpful nudges to keep you on track.

    Made with ❤️ using Python, Streamlit, Matplotlib, Pandas and some hard work.
    """)
