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
                amount = None
                amount_match = re.search(r'(?:INR|₹|Rs\.?|rs)?[\s]*([\d,]+(?:\.\d{1,2})?)', sms, re.IGNORECASE)
                if amount_match and amount_match.group(1).strip():
                    try:
                        amount = float(amount_match.group(1).replace(",", ""))
                    except ValueError:
                        amount = None

                merchant_match = re.search(r'(?:at|for|on|from)\s+([A-Za-z&]+)', sms, re.IGNORECASE)
                merchant = merchant_match.group(1).title() if merchant_match else "Unknown"

                if "debited" in sms.lower() or "spent" in sms.lower():
                    txn_type = "Debit"
                elif "credited" in sms.lower():
                    txn_type = "Credit"
                elif "declined" in sms.lower() or "reversed" in sms.lower():
                    txn_type = "Reversal"
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
