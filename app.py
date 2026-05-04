import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import os
import threading
import random
import time
from io import StringIO
import agent
import RAG_pipeline as rag
import data_fetcher as df

st.set_page_config(
    page_title="FinSight AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Theme Toggle ---
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

_, theme_col = st.columns([10, 1])
with theme_col:
    if st.button("🌙" if st.session_state.dark_mode else "☀️"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

if st.session_state.dark_mode:
    bg = "#0B0E11"
    secondary_bg = "#151A1E"
    text = "#FFFFFF"
    accent = "#00D4AA"
    tape_color = "#00D4AA"
else:
    bg = "#FFFFFF"
    secondary_bg = "#F5F5F5"
    text = "#000000"
    accent = "#0066CC"
    tape_color = "#0066CC"

st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg}; color: {text}; }}
        .stButton button {{ 
            background: {accent}; 
            color: {'black' if st.session_state.dark_mode else 'white'}; 
            font-weight: 700; 
            border-radius: 8px;
            font-size: 16px;
        }}
        .stButton button:hover {{ opacity: 0.85; }}
    </style>
""", unsafe_allow_html=True)

NIFTY50_CSV = "nifty50.csv"
FALLBACK = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'WIPRO.NS',
            'ICICIBANK.NS', 'KOTAKBANK.NS', 'HINDUNILVR.NS', 'AXISBANK.NS']

def fetch_nifty50_from_nse():
    url = "https://nsearchives.nseindia.com/content/indices/ind_nifty50list.csv"
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.nseindia.com"}
    with requests.Session() as session:
        session.headers.update(headers)
        session.get("https://www.nseindia.com", timeout=5)
        response = session.get(url, timeout=10)
        df_csv = pd.read_csv(StringIO(response.content.decode('utf-8')))
        tickers = [s + ".NS" for s in df_csv['Symbol'].tolist()]
        pd.DataFrame({"symbol": tickers}).to_csv(NIFTY50_CSV, index=False)
        return tickers

def load_tickers():
    if os.path.exists(NIFTY50_CSV):
        return pd.read_csv(NIFTY50_CSV)['symbol'].tolist()
    return FALLBACK

def refresh_tickers_background():
    try:
        fetch_nifty50_from_nse()
    except:
        pass

@st.cache_data(ttl=300)
def get_tape_data(tickers):
    tape = ""
    for symbol in tickers[:10]:
        try:
            t = yf.Ticker(symbol)
            price = t.fast_info['last_price']
            prev = t.fast_info['previous_close']
            change = price - prev
            pct = (change / prev) * 100
            arrow = "▲" if change >= 0 else "▼"
            tape += f"{symbol} ₹{price:.2f} {arrow} {pct:.2f}%   |   "
        except:
            pass
    return tape

def plain_english_valuation(pe):
    if pe is None or pe == 0: return "Unknown"
    elif pe < 15: return "🟢 Cheap"
    elif pe < 25: return "🟡 Fair price"
    elif pe < 40: return "🟠 Expensive"
    else: return "🔴 Very expensive"

def plain_english_risk(beta):
    if beta is None: return "Unknown"
    elif beta < 0.5: return "🟢 Very low risk"
    elif beta < 1: return "🟡 Low risk"
    elif beta < 1.5: return "🟠 Medium risk"
    else: return "🔴 High risk"

def plain_english_range(price, high, low):
    try:
        position = ((price - low) / (high - low)) * 100
        if position < 30: return "🟢 Near low ✅"
        elif position < 70: return "🟡 Mid range"
        else: return "🔴 Near high ⚠️"
    except:
        return "Unknown"

# Session state
for key in ["ticker", "analysis", "fundamentals", "news", "intent"]:
    if key not in st.session_state:
        st.session_state[key] = None

# Ticker tape
tape_placeholder = st.empty()

# Header
_, mid, _ = st.columns([1, 3, 1])
with mid:
    st.markdown("## 📊 FinSight AI")
    st.markdown("##### Know whether to Buy, Sell or Hold — in seconds.")
    st.markdown("<br>", unsafe_allow_html=True)
    ticker_input = st.text_input(
        "",
        placeholder="Type a stock ticker e.g. RELIANCE.NS",
        label_visibility="collapsed"
    )
    go = st.button("Get Analysis →", use_container_width=True)

st.markdown("---")

# Load ticker tape
tickers = load_tickers()
threading.Thread(target=refresh_tickers_background, daemon=True).start()
tape = get_tape_data(tuple(tickers[:10]))
tape_placeholder.markdown(
    f'<marquee behavior="scroll" direction="left" scrollamount="3" '
    f'style="background:{secondary_bg}; color:{tape_color}; padding:10px; '
    f'font-family:monospace; font-size:13px;">{tape}</marquee>',
    unsafe_allow_html=True
)

# Step 1 — ticker entered
if go and ticker_input:
    st.session_state.ticker = ticker_input.upper().strip()
    st.session_state.intent = None
    st.session_state.analysis = None
    st.session_state.fundamentals = None
    st.session_state.news = None
elif go and not ticker_input:
    st.warning("Please type a stock ticker first!")

# Step 2 — ask intent with 2 buttons
if st.session_state.ticker and st.session_state.intent is None:
    _, intent_col, _ = st.columns([1, 2, 1])
    with intent_col:
        st.markdown(f"### Do you own **{st.session_state.ticker}**?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Yes, I own it", use_container_width=True):
                st.session_state.intent = "own"
                st.rerun()
        with c2:
            if st.button("🔍 No, considering buying", use_container_width=True):
                st.session_state.intent = "buying"
                st.rerun()

# Step 3 — run pipeline
if st.session_state.ticker and st.session_state.intent and st.session_state.analysis is None:
    stock = yf.Ticker(st.session_state.ticker)

    _, loading_col, _ = st.columns([1, 2, 1])
    with loading_col:
        st.markdown(f"### 🔍 Analysing **{st.session_state.ticker}**")
        st.markdown("---")

        step1 = st.empty()
        step2 = st.empty()
        step3 = st.empty()
        step4 = st.empty()
        step5 = st.empty()
        done = st.empty()

        step1.markdown("⏳ Getting live stock price...")
        fundamentals = df.get_fundamentals(stock)
        step1.markdown("✅ Got live price and key numbers")

        step2.markdown("⏳ Downloading financial statements...")
        financials_text = df.financials_to_text(stock)
        step2.markdown("✅ Downloaded quarterly financials")

        step3.markdown("⏳ Fetching latest news...")
        news = df.get_news(stock)
        st.session_state.fundamentals = fundamentals
        st.session_state.news = news
        step3.markdown("✅ Found latest news headlines")

        step4.markdown("⏳ Teaching AI about this company...")
        combined = rag.prepare_text(fundamentals, financials_text, news)
        chunks = rag.chunk_text(combined)
        vectorstore = rag.create_vector_store(chunks)
        results = rag.search_vectorstore(vectorstore, f"buy sell hold {st.session_state.ticker}")
        step4.markdown("✅ AI has studied the company")

        step5.markdown("⏳ Getting personalised verdict...")
        prompt = agent.build_prompt(f"Analyse {st.session_state.ticker}", results, st.session_state.intent)
        st.session_state.analysis = agent.generate_analysis(prompt)
        step5.markdown("✅ Verdict is ready!")

        time.sleep(1)
        step1.empty(); step2.empty(); step3.empty()
        step4.empty(); step5.empty()
        done.markdown("### 🎯 See your verdict below ↓")
        time.sleep(1)
        done.empty()

# Step 4 — display results
if st.session_state.analysis:
    analysis = st.session_state.analysis
    fundamentals = st.session_state.fundamentals
    news = st.session_state.news
    intent = st.session_state.intent

    name = fundamentals.get("name", st.session_state.ticker)
    price = fundamentals.get("current_price", "N/A")
    pe = fundamentals.get("trailing_pe") or 0
    high = fundamentals.get("52w_high") or 0
    low = fundamentals.get("52w_low") or 0
    beta = fundamentals.get("beta")
    confidence = analysis.get("confidence", 0)
    verdict = analysis.get("verdict", "HOLD")
    reason = analysis.get("reason", "")

    # Company header
    st.markdown(f"### {name}")
    st.caption(analysis.get("summary", ""))
    st.markdown("<br>", unsafe_allow_html=True)

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Current Price", f"₹{price}")
    c2.metric("🏷️ Is it expensive?", plain_english_valuation(pe))
    c3.metric("📅 In yearly range", plain_english_range(price, high, low))
    c4.metric("⚡ How risky?", plain_english_risk(beta))

    st.markdown("---")

    # Verdict
    st.markdown("### 🎯 Our Verdict")

    if intent == "own":
        # Already owns it — Hold or Sell
        if verdict == "HOLD":
            st.success("# 📈 KEEP HOLDING")
            st.markdown(f"**Why?** {reason}")
        else:
            st.error("# 🚨 CONSIDER SELLING")
            st.markdown(f"**Why?** {reason}")
    else:
        # Considering buying — Buy or Wait
        if verdict == "BUY":
            st.success("# ✅ GOOD TIME TO BUY")
            st.markdown(f"**Why?** {reason}")
        else:
            st.warning("# ⏳ WAIT — NOT YET")
            st.markdown(f"**Why?** {reason}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption(f"🧠 AI Confidence: {confidence}%")
    st.progress(confidence / 100)

    st.markdown("---")

    # Key risk
    st.markdown("### ⚠️ Biggest Risk Right Now")
    st.warning(analysis.get("key_risk", "N/A"))

    st.markdown("---")

    # News
    st.markdown("### 📰 What's happening")
    for item in news[:3]:
        with st.container(border=True):
            st.markdown(f"**{item['title']}**")
            st.caption(item['summary'][:180] + "...")

    # Analyse another stock
    st.markdown("---")
    if st.button("🔄 Analyse Another Stock", use_container_width=True):
        for key in ["ticker", "analysis", "fundamentals", "news", "intent"]:
            st.session_state[key] = None
        st.rerun()