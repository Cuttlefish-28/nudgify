import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_lottie import st_lottie
import requests
import random
from streamlit_option_menu import option_menu
from PIL import Image

from io import BytesIO

# ---------- Lottie Animation Helper ----------
import streamlit_lottie as st_lottie

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# ---------- Lottie Animations ----------
save_money = load_lottieurl("https://lottie.host/19a15030-865b-4c47-87a5-6b7c8b9d4f80/QTFnpoId4G.json")
spend_money = load_lottieurl("https://lottie.host/2e314846-eabf-4973-9499-b27e5aadb79b/qIYZmLEtuH.json")

def get_nudge(category):
    nudges = {
        "Food": [
            "Zomato again? Your kitchen’s developing abandonment issues.",
            "Swiggy is not your soulmate. Try home-cooked love.",
            "Calories: 1000, Regret: 10,000."
        ],
        "Shopping": [
            "You don’t need that. You want it. Your wallet disagrees.",
            "Adding to cart ≠ adding value.",
            "You’re not broke. You’re just fashion-forward… and broke."
        ],
        "Coffee": [
            "₹350 for coffee? Brew it at home, barista BAE.",
            "You could buy a coffee machine by now."
        ],
        "Travel": [
            "Taking Uber like you’re Elon Musk?",
            "Wheels down, savings gone.",
            "You’re not flying private. But your money just vanished."
        ],
        "Alcohol": [
            "Saturday night fun = Sunday morning regrets (and expenses).",
            "Your liver and wallet are both screaming."
        ],
        "Subscriptions": [
            "Still paying for Hotstar, Prime, Netflix, and… what’s Voot?",
            "You’ve got more subscriptions than hobbies."
        ],
        "Gaming": [
            "Fun is temporary. Debt is not.",
            "Your game rank went up, your bank balance went down."
        ],
        "Dating": [
            "Dating is expensive. Consider falling in love with saving.",
            "You paid for their meal *and* the emotional damage."
        ],
        "Books": [
            "Okay, nerd. Approved. Carry on.",
            "Knowledge is power. But check if Coursera is on discount."
        ]
    }
    return random.choice(nudges.get(category, ["Spending looks sus 👀"]))

# ---------- Category Extraction (Example) ----------
def extract_category(merchant):
    merchant = merchant.lower()
    if any(x in merchant for x in ["zomato", "swiggy", "food"]):
        return "Food"
    elif any(x in merchant for x in ["amazon", "flipkart", "myntra"]):
        return "Shopping"
    elif any(x in merchant for x in ["starbucks", "coffee"]):
        return "Coffee"
    elif any(x in merchant for x in ["uber", "ola", "air"]):
        return "Travel"
    elif any(x in merchant for x in ["bar", "pub", "beer"]):
        return "Alcohol"
    elif any(x in merchant for x in ["netflix", "prime", "hotstar"]):
        return "Subscriptions"
    elif any(x in merchant for x in ["game", "steam"]):
        return "Gaming"
    elif any(x in merchant for x in ["tinder", "bumble"]):
        return "Dating"
    elif any(x in merchant for x in ["book", "coursera"]):
        return "Books"
    else:
        return "Other"

# ---------- Sidebar Navigation ----------
with st.sidebar:
    selected = option_menu(
        "Nudgify App 💡", ["Home", "Upload CSV", "About"],
        icons=["house", "upload", "info-circle"],
        menu_icon="sparkles", default_index=0
    )

# ---------- Home Page ----------
if selected == "Home":
    st.title("Nudgify 💸 | Spend Smarter, Live Better")
    col1, col2 = st.columns(2)
    with col1:
        st_lottie.st_lottie(save_money, speed=1, height=400, key="save")
    with col2:
        st.markdown("### Welcome to Nudgify!")
        st.markdown("We're here to roast your purchases and help you save cash with Gen Z vibes 🔥")

# ---------- Upload Page ----------
elif selected == "Upload CSV":
    st.header("📤 Upload your Expense CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        if 'Merchant' not in df.columns:
            st.error("CSV must contain a 'Merchant' column.")
        else:
            df['Category'] = df['Merchant'].apply(extract_category)
            df['Nudge'] = df['Category'].apply(get_nudge)

            st.success("Nudges Generated 🎉")

            with st.container():
                for i, row in df.iterrows():
                    with st.expander(f"{row['Merchant']} | ₹{row.get('Amount', 'NA')} - {row['Category']}"):
                        st.write(f"💬 {row['Nudge']}")

# ---------- About Page ----------
elif selected == "About":
    st.header("💡 About Nudgify")
    st.markdown("Nudgify is your Gen-Z spending conscience. Built using Streamlit, Lottie, and pure sass ✨")

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
