import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="Trading Support Dashboard", layout="wide")

# News API (replace with your key)
NEWS_API_KEY = st.secrets.get("NEWS_API_KEY", "your_free_key_here")
NEWS_URL = f"https://newsapi.org/v2/everything?q=india+stock+market&apiKey={NEWS_API_KEY}&sortBy=publishedAt&pageSize=10"

@st.cache_data(ttl=60)  # Refresh every minute
def get_live_data(symbols=["^NSEI", "^BSESN"]):  # NIFTY50, SENSEX
    data = {}
    for sym in symbols:
        ticker = yf.Ticker(sym)
        info = ticker.info
        hist = ticker.history(period="1d", interval="1m")
        if not hist.empty:
            data[sym] = {
                'high': hist['High'].max(),
                'low': hist['Low'].min(),
                'ltp': info.get('regularMarketPrice', hist['Close'][-1]),
                'change': info.get('regularMarketChangePercent', 0)
            }
    return data

@st.cache_data(ttl=300)
def get_news():
    try:
        resp = requests.get(NEWS_URL)
        return resp.json().get('articles', [])[:5]
    except:
        return []

# Sidebar for tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Live Market", "📰 Latest News", "💬 FAQ/Query Solver", "📚 Support Skills"])

with tab1:
    st.header("NSE/BSE Live High/Low")
    symbols = st.multiselect("Select Indices/Stocks", ["^NSEI", "^BSESN", "RELIANCE.NS", "TCS.NS"], default=["^NSEI", "^BSESN"])
    data = get_live_data(symbols)
    df = pd.DataFrame(data).T
    st.dataframe(df.round(2), use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df.index, y=df['high'], name='High'))
        fig.add_trace(go.Bar(x=df.index, y=df['low'], name='Low'))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.metric("NIFTY Day Range", f"{df.loc['^NSEI', 'low']:.2f} - {df.loc['^NSEI', 'high']:.2f}")

with tab2:
    st.header("Live Market News")
    articles = get_news()
    for art in articles:
        st.markdown(f"**{art['title']}** [web:3]")
        st.caption(art['description'])
        st.caption(art['url'])

with tab3:
    st.header("Demat/Trading FAQ Solver")
    query = st.text_input("Ask about demat issues (e.g., 'funds not visible')")
    faqs = {
        "login issues": "Check password/OTP; no multi-login. Reset via app.",
        "funds transfer": "Verify bank details; check banking hours.",
        "holdings not visible": "Wait T+1 settlement; contact DP if off-market.",
        "order rejected": "Insufficient balance or restrictions."
    }  # From common queries [web:4][web:10]
    if query.lower() in faqs:
        st.success(faqs[query.lower()])
    st.markdown("**Top Queries:**")
    for q, a in faqs.items():
        with st.expander(q.title()):
            st.write(a)

with tab4:
    st.header("Support Skills Toolkit")
    
    # Email Generator
    st.subheader("📧 Email Templates")
    issue = st.selectbox("Issue Type", ["Funds Issue", "Login Problem", "General Query"])
    customer_name = st.text_input("Customer Name")
    if st.button("Generate Email"):
        template = f"""
Hello {customer_name},

Thank you for contacting us. We understand your {issue.lower()} concern.

- Solution: [Insert steps, e.g., Verify bank for funds].
- Next: Reply with details or call 1800-XXX.

Best, Support Team
        """.strip()
        st.code(template)  # Copy-paste ready [web:12][web:16]
    
    # Call Scripts
    st.subheader("📞 Call Handling Scripts")
    script_type = st.selectbox("Script", ["Greeting", "Issue Resolution", "Transfer"])
    scripts = {
        "greeting": "Hello [Name], this is Support. How can I assist with your demat account today?",
        "issue resolution": "I see the issue. Let's fix: Step 1... Does that resolve it?",
        "transfer": "I'll transfer to trading desk. Hold briefly."
    }  # Adapted from best practices [web:6][web:13]
    st.info(scripts[script_type])
    
    # Quick Learn
    st.subheader("🔍 Tips")
    st.markdown("- **Emails**: Empathetic tone + clear steps + CTA [web:5].")
    st.markdown("- **Calls**: Active listen, confirm understanding, end positive [web:13].")
