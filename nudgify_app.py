import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_lottie import st_lottie
import requests
import re
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

    # ---------- TABS ----------
    tab1, tab2, tab3 = st.tabs(["📂 Upload", "📊 Insights", "💡 Nudges"])

with tab1:
    st.subheader("Upload CSV or Paste SMS Messages")

    # 📂 CSV Upload
    uploaded_file = st.file_uploader("Upload your transaction CSV", type="csv")
    
    # 📝 Paste SMS messages manually
    sms_input = st.text_area("Or paste your SMS messages (one per line)", height=200)
    
    df = None  # initialize empty df for use later

    # 📄 If CSV uploaded
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.columns = df.columns.str.strip().str.title()
        if 'Merchant' in df.columns and 'Category' not in df.columns:
            merchant_to_category = {
                'Zomato': 'Food', 'Swiggy': 'Food', 'Amazon': 'Shopping',
                'Uber': 'Transport', 'Blinkit': 'Groceries', 'H&M': 'Clothing'
            }
            df['Merchant'] = df['Merchant'].str.strip().str.title()
            df['Category'] = df['Merchant'].map(lambda x: merchant_to_category.get(x, 'Others'))
        st.success("✅ File uploaded successfully!")
        st.dataframe(df.head())

    # 📄 If SMS pasted
    elif sms_input:
        sms_lines = sms_input.strip().split('\n')

        parsed_data = []
        for sms in sms_lines:
            amount_match = re.search(r'(INR|₹|Rs\\.?|rs)?\\s?(\\d+[.,]?\\d*)', sms, re.IGNORECASE)
            amount = float(amount_match.group(2)) if amount_match else None

            merchant_match = re.search(r'(at|for|on|from)\\s+([A-Za-z&]+)', sms, re.IGNORECASE)
            merchant = merchant_match.group(2).title() if merchant_match else \"Unknown\"

            if \"debited\" in sms.lower() or \"spent\" in sms.lower():
                txn_type = \"Debit\"
            elif \"credited\" in sms.lower():
                txn_type = \"Credit\"
            else:
                txn_type = \"Unknown\"

            parsed_data.append({
                \"Merchant\": merchant,
                \"Amount\": amount,
                \"Type\": txn_type,
                \"Message\": sms
            })

        df = pd.DataFrame(parsed_data)
        st.success(\"✅ SMS parsed successfully!\")
        st.dataframe(df)

   with tab2:
    if df is not None and 'Amount' in df.columns:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        df.dropna(subset=['Amount'], inplace=True)

        # ✅ Generate category from merchant if not already present
        if 'Category' not in df.columns and 'Merchant' in df.columns:
            merchant_to_category = {
                'Swiggy': 'Food', 'Zomato': 'Food', 'Dominos': 'Food',
                'Amazon': 'Shopping', 'Flipkart': 'Shopping', 'Nykaa': 'Beauty',
                'Uber': 'Transport', 'Rapido': 'Transport',
                'H&M': 'Clothing', 'Myntra': 'Clothing',
            }
            df['Merchant'] = df['Merchant'].str.strip().str.title()
            df['Category'] = df['Merchant'].map(lambda x: merchant_to_category.get(x, 'Others'))

        # ✅ Now plot category-wise spend
        if 'Category' in df.columns:
            st.subheader("📍 Category Breakdown")
            category_spend = df.groupby('Category')['Amount'].sum()
            fig, ax = plt.subplots()
            category_spend.plot(kind='pie', autopct='%1.1f%%', ax=ax)
            ax.set_ylabel("")
            st.pyplot(fig)
                    # 🔢 Ask for budget if not already set
        st.subheader("📈 Budget Usage")
        user_budget_insight = st.number_input("Enter your monthly budget (₹):", min_value=0, value=15000, step=500, key="budget_tab2")

        total_spent = df['Amount'].sum()
        percent_spent = (total_spent / user_budget_insight) * 100

         if percent_spent >= 100:
            st.error(f"🚨 You've spent {percent_spent:.1f}% of your monthly budget. You're over the limit!")
         elif percent_spent >= 80:
            st.warning(f"⚠️ {percent_spent:.1f}% of your budget is already used. Slow down a little?")
         elif percent_spent >= 50:
            st.info(f"⏳ You've used {percent_spent:.1f}% of your budget. Track weekly to stay in control.")
         else:
            st.success(f"💚 Only {percent_spent:.1f}% of your budget spent — keep going smart!")

        else:
            st.warning("🟨 No 'Category' column found.")


    with tab3:
        
            if uploaded_file or sms_input:
    if df is not None and 'Amount' in df.columns:
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        df.dropna(subset=['Amount'], inplace=True)

        # 🧠 Ask for Monthly Budget
        st.subheader("🎯 Set Your Monthly Budget")
        user_budget = st.number_input("Enter your monthly budget (₹):", min_value=0, value=15000, step=500)

        total_spend = df['Amount'].sum()
        avg_spend = df['Amount'].mean()
        debit_spends = df[df['Type'] == 'Debit']['Amount'].sum()
        credit_spends = df[df['Type'] == 'Credit']['Amount'].sum()
        food_spends = df[df['Merchant'].str.contains('Swiggy|Zomato|Dominos|Pizza', case=False, na=False)]['Amount'].sum()

        st.subheader("📊 Summary")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### 💰 Total Spend")
            st.markdown(f"<div class='card'>₹ {total_spend:.2f}</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("#### 📉 Average Spend")
            st.markdown(f"<div class='card'>₹ {avg_spend:.2f}</div>", unsafe_allow_html=True)

        with col3:
            st.markdown("#### 🧾 Monthly Budget")
            st.markdown(f"<div class='card'>₹ {user_budget:.2f}</div>", unsafe_allow_html=True)

        st.markdown("### 💡 Nudgify Says:")

        # 🚦 Smart Nudges
        if total_spend > user_budget:
            st.error("🚨 Over Budget! Chill out a bit — maybe time for some Maggi nights?")
        elif total_spend > 0.8 * user_budget:
            st.warning("🟨 Budget danger zone! You're almost at your limit. Breathe before that next UPI tap.")
        elif total_spend < 0.5 * user_budget:
            st.success("💚 You're doing great! Maybe use the extra cash to build an emergency fund or invest.")

        if avg_spend > 1000:
            st.info("🛍️ You seem to be spending in chunks. Consider spreading purchases or tracking subscriptions.")
        if food_spends > 0.25 * total_spend:
            st.warning("🍔 Foodie Alert! You've spent over 25% on food. Try cooking challenges for fun & savings.")

        if credit_spends > debit_spends:
            st.warning("💳 More money is coming in than going out. Plan what to do with that surplus smartly!")
        elif debit_spends > 2 * credit_spends:
            st.error("😰 You're bleeding money! Consider cutting down variable spends next month.")

        if 'Amazon' in df['Merchant'].values.tolist():
            st.info("📦 Frequent Amazon activity — add to wishlist instead of cart for 3 days rule!")

        if len(df) > 30:
            st.success("📆 You're financially active! Consider weekly review goals to track better.")
        user_budget = st.number_input(...)  # already in your code
        total_spend = df['Amount'].sum()
        avg_daily_budget = user_budget / 30
        # 📅 Calculate today's spend if date exists
   if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    today = pd.Timestamp.today().normalize()
    today_spend = df[df['Date'] == today]['Amount'].sum()

    if today_spend > avg_daily_budget:
        st.error(f"⚠️ Daily limit crossed! You spent ₹{today_spend:.2f} today, more than your ₹{avg_daily_budget:.0f}/day budget.")
    elif today_spend > 0:
        st.info(f"🧠 You're at ₹{today_spend:.2f} today. Keep it under ₹{avg_daily_budget:.0f} to stay chill.")
   # 🔁 Repeat merchants
merchant_counts = df['Merchant'].value_counts()

repeat_merchants = merchant_counts[merchant_counts >= 3].index.tolist()
for merchant in repeat_merchants:
    if merchant.lower() in ['swiggy', 'zomato']:
        st.warning(f"🍟 Too much {merchant}? You ordered {merchant_counts[merchant]} times. Time to explore your kitchen?")
    elif merchant.lower() in ['amazon', 'flipkart', 'nykaa']:
        st.info(f"🛒 Frequent {merchant} purchases! Try the 3-day rule before checkout.")



        st.balloons()

# ------------------ ABOUT PAGE ------------------
if selected == "About":
    st.title("👩‍💻 About Nudgify")
    st.markdown("""
    Nudgify is your Gen Z friendly personal spending advisor 🧠💸.
    It reads your expenses, finds patterns, and gives cheeky yet helpful nudges to keep you on track.

    Made with ❤️ using Python, Streamlit, Matplotlib, Pandas and some hardwork.
    """)

