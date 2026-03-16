import streamlit as st
import yfinance as yf
import feedparser
from datetime import datetime
import time

# ---------- Page config ----------
st.set_page_config(page_title="Nifty Live Dashboard", layout="wide")

# ---------- Title ----------
st.title("📊 Nifty 50 Live Dashboard")
st.markdown("---")

# ---------- Auto-refresh every 5 seconds ----------
from streamlit_autorefresh import st_autorefresh
refresh_count = st_autorefresh(interval=5 * 1000, key="auto")

# ---------- Helper: Fetch Nifty data ----------
@st.cache_data(ttl=5)  # cache for 5 seconds
def get_nifty_data():
    try:
        ticker = yf.Ticker("^NSEI")
        data = ticker.history(period="1d", interval="1m")
        if data.empty:
            # Fallback if no data
            return {
                "price": 0,
                "high": 0,
                "low": 0,
                "change": 0,
                "change_percent": 0,
                "time": datetime.now()
            }
        latest = data.iloc[-1]
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else latest['Close']
        change = latest['Close'] - prev_close
        change_percent = (change / prev_close) * 100
        return {
            "price": round(latest['Close'], 2),
            "high": round(data['High'].max(), 2),
            "low": round(data['Low'].min(), 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "time": datetime.now()
        }
    except Exception as e:
        st.error(f"Error fetching Nifty data: {e}")
        # Return dummy data so dashboard doesn't break
        return {
            "price": 18500.00,
            "high": 18600.00,
            "low": 18400.00,
            "change": 25.00,
            "change_percent": 0.14,
            "time": datetime.now()
        }

# ---------- Helper: Fetch news headlines ----------
@st.cache_data(ttl=300)  # cache for 5 minutes
def get_news():
    try:
        feed = feedparser.parse("https://economictimes.indiatimes.com/rssfeedsdefault.cms?feed=news")
        headlines = []
        for entry in feed.entries[:10]:
            headlines.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published
            })
        return headlines
    except:
        # fallback headlines
        return [
            {"title": "RBI keeps repo rate unchanged", "link": "#", "published": "Just now"},
            {"title": "IT stocks rally on strong earnings", "link": "#", "published": "1 hour ago"},
        ]

# ---------- Fetch data ----------
nifty = get_nifty_data()
news = get_news()

# ---------- Layout: Nifty metrics ----------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Nifty 50", f"₹ {nifty['price']}", f"{nifty['change']} ({nifty['change_percent']}%)")
with col2:
    st.metric("Day High", f"₹ {nifty['high']}")
with col3:
    st.metric("Day Low", f"₹ {nifty['low']}")
with col4:
    st.metric("Last Updated", nifty['time'].strftime("%H:%M:%S"))

st.markdown("---")

# ---------- News section ----------
st.subheader("📰 Latest Business News (India)")
for item in news:
    with st.expander(item['title']):
        st.write(f"Published: {item['published']}")
        st.markdown(f"[Read full article]({item['link']})")

st.markdown("---")

# ---------- Chatbot FAQ ----------
st.subheader("💬 Trading FAQ Chatbot")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! Ask me about trading (e.g., 'account opening', 'trading hours')"}
    ]

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Your question:"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate response (simple keyword matching)
    lower = prompt.lower()
    response = "I can help with account opening, trading hours, settlement, margin, and Nifty basics. Please ask a specific question."
    faq = {
        "account opening": "You can open an account online with any SEBI registered broker. Required documents: PAN, Aadhaar, bank details.",
        "trading hours": "Equity market timings: Monday to Friday, 9:15 AM to 3:30 PM (except holidays).",
        "settlement": "T+1 settlement cycle – shares credited to demat next day, funds after one day.",
        "margin": "Margin depends on broker and segment. Typically 20-50% for intraday.",
        "nifty": "Nifty 50 is the benchmark index of NSE, representing top 50 companies.",
    }
    for key, ans in faq.items():
        if key in lower:
            response = ans
            break

    # Simulate thinking
    time.sleep(0.5)
    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)
