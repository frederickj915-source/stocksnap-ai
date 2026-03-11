import streamlit as st
import yfinance as yf
import pandas as pd
from openai import OpenAI

st.set_page_config(page_title="StockSnap AI", page_icon="📈", layout="wide")

st.title("📈 StockSnap AI")
st.caption("AI-powered stock comparison and single-stock analysis tool")
st.divider()

st.write("Use real market data, growth trends, and AI summaries to analyze stocks.")

ai_stock_list = ["NVDA", "AMD", "MSFT", "GOOGL", "AMZN", "TSM", "META", "AAPL"]

st.subheader("🔥 Top AI Stocks")
selected_ai_stock = st.selectbox(
    "Pick a popular AI-related stock for quick analysis:",
    ["None"] + ai_stock_list
)

mode = st.radio("Choose analysis mode:", ["Compare Two Stocks", "Analyze One Stock"])

if mode == "Compare Two Stocks":
    ticker1 = st.text_input("Enter first stock ticker", value="NVDA").upper()
    ticker2 = st.text_input("Enter second stock ticker", value="AMD").upper()
else:
    default_single = selected_ai_stock if selected_ai_stock != "None" else "NVDA"
    single_ticker = st.text_input("Enter a stock ticker", value=default_single).upper()


def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    income_stmt = stock.financials

    revenue = "N/A"
    net_income = "N/A"
    revenue_growth = "N/A"
    earnings_growth = "N/A"
    gross_margin = "N/A"
    operating_margin = "N/A"

    if not income_stmt.empty:
        if "Total Revenue" in income_stmt.index:
            revenue_series = income_stmt.loc["Total Revenue"]
            revenue = revenue_series.iloc[0]
            if len(revenue_series) > 1 and revenue_series.iloc[1] not in [0, None]:
                revenue_growth = ((revenue_series.iloc[0] - revenue_series.iloc[1]) / revenue_series.iloc[1]) * 100

        if "Net Income" in income_stmt.index:
            income_series = income_stmt.loc["Net Income"]
            net_income = income_series.iloc[0]
            if len(income_series) > 1 and income_series.iloc[1] not in [0, None]:
                earnings_growth = ((income_series.iloc[0] - income_series.iloc[1]) / income_series.iloc[1]) * 100

        if "Gross Profit" in income_stmt.index and "Total Revenue" in income_stmt.index:
            gross_profit = income_stmt.loc["Gross Profit"].iloc[0]
            total_revenue = income_stmt.loc["Total Revenue"].iloc[0]
            if total_revenue not in [0, None]:
                gross_margin = (gross_profit / total_revenue) * 100

        if "Operating Income" in income_stmt.index and "Total Revenue" in income_stmt.index:
            operating_income = income_stmt.loc["Operating Income"].iloc[0]
            total_revenue = income_stmt.loc["Total Revenue"].iloc[0]
            if total_revenue not in [0, None]:
                operating_margin = (operating_income / total_revenue) * 100

    hist = stock.history(period="6mo")
    latest_close = hist["Close"].iloc[-1] if not hist.empty else "N/A"

    return {
        "Company": info.get("longName", "N/A"),
        "Ticker": ticker,
        "Price": info.get("currentPrice", latest_close),
        "Market Cap": info.get("marketCap", "N/A"),
        "P/E Ratio": info.get("trailingPE", "N/A"),
        "Sector": info.get("sector", "N/A"),
        "Revenue": revenue,
        "Revenue Growth %": revenue_growth,
        "Net Income": net_income,
        "Earnings Growth %": earnings_growth,
        "Gross Margin %": gross_margin,
        "Operating Margin %": operating_margin,
        "History": hist
    }


def get_market_signal(stock):
    score = 0

    rev_growth = stock["Revenue Growth %"]
    earn_growth = stock["Earnings Growth %"]
    pe = stock["P/E Ratio"]
    gross_margin = stock["Gross Margin %"]
    op_margin = stock["Operating Margin %"]

    if rev_growth != "N/A":
        if rev_growth > 20:
            score += 2
        elif rev_growth > 5:
            score += 1
        elif rev_growth < 0:
            score -= 1

    if earn_growth != "N/A":
        if earn_growth > 20:
            score += 2
        elif earn_growth > 5:
            score += 1
        elif earn_growth < 0:
            score -= 1

    if pe != "N/A":
        if pe < 25:
            score += 1
        elif pe > 60:
            score -= 1

    if gross_margin != "N/A":
        if gross_margin > 50:
            score += 1
        elif gross_margin < 20:
            score -= 1

    if op_margin != "N/A":
        if op_margin > 20:
            score += 1
        elif op_margin < 5:
            score -= 1

    if score >= 5:
        return "🟢 Bullish"
    elif score >= 2:
        return "🟡 Neutral"
    else:
        return "🔴 Risky"


if mode == "Compare Two Stocks" and st.button("Analyze Stocks"):
    stock1 = get_stock_data(ticker1)
    stock2 = get_stock_data(ticker2)

    df = pd.DataFrame([
        {k: v for k, v in stock1.items() if k != "History"},
        {k: v for k, v in stock2.items() if k != "History"}
    ])

    st.subheader("Stock Comparison")
    st.dataframe(df, width="stretch")

    st.subheader("Market Signal")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label=f"{ticker1} Signal", value=get_market_signal(stock1))
    with col2:
        st.metric(label=f"{ticker2} Signal", value=get_market_signal(stock2))

    st.subheader("6-Month Price Trend")

    if not stock1["History"].empty:
        st.write(f"{ticker1} price chart")
        st.line_chart(stock1["History"]["Close"])

    if not stock2["History"].empty:
        st.write(f"{ticker2} price chart")
        st.line_chart(stock2["History"]["Close"])

    st.subheader("AI Summary")
    st.info("AI-generated comparison for educational purposes only. Not financial advice.")

    if "OPENAI_API_KEY" not in st.secrets:
        st.error("OPENAI_API_KEY is missing in Streamlit Secrets.")
    else:
        prompt = f"""
Compare these two stocks for a beginner investor.

Stock 1:
Company: {stock1["Company"]}
Ticker: {stock1["Ticker"]}
Price: {stock1["Price"]}
Market Cap: {stock1["Market Cap"]}
P/E Ratio: {stock1["P/E Ratio"]}
Sector: {stock1["Sector"]}
Revenue: {stock1["Revenue"]}
Revenue Growth %: {stock1["Revenue Growth %"]}
Net Income: {stock1["Net Income"]}
Earnings Growth %: {stock1["Earnings Growth %"]}
Gross Margin %: {stock1["Gross Margin %"]}
Operating Margin %: {stock1["Operating Margin %"]}
Market Signal: {get_market_signal(stock1)}

Stock 2:
Company: {stock2["Company"]}
Ticker: {stock2["Ticker"]}
Price: {stock2["Price"]}
Market Cap: {stock2["Market Cap"]}
P/E Ratio: {stock2["P/E Ratio"]}
Sector: {stock2["Sector"]}
Revenue: {stock2["Revenue"]}
Revenue Growth %: {stock2["Revenue Growth %"]}
Net Income: {stock2["Net Income"]}
Earnings Growth %: {stock2["Earnings Growth %"]}
Gross Margin %: {stock2["Gross Margin %"]}
Operating Margin %: {stock2["Operating Margin %"]}
Market Signal: {get_market_signal(stock2)}

Return your answer in this exact format:

## StockSnap AI Rating

### {stock1["Ticker"]}
- Rating: BUY, HOLD, or RISKY
- Overall Score: x/10
- Growth Score: x/10
- Valuation Score: x/10
- Profitability Score: x/10
- Risk Score: x/10
- Market Signal: {get_market_signal(stock1)}

### {stock2["Ticker"]}
- Rating: BUY, HOLD, or RISKY
- Overall Score: x/10
- Growth Score: x/10
- Valuation Score: x/10
- Profitability Score: x/10
- Risk Score: x/10
- Market Signal: {get_market_signal(stock2)}

## Winner
State which stock looks stronger right now and why in 2-3 sentences.

## Beginner Summary
Give a short beginner-friendly summary with key risks for both stocks.

Keep spacing clean and easy to read.
Not financial advice.
"""

        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )
            st.markdown(response.output_text)
        except Exception as e:
            st.error(f"AI summary could not load: {e}")


if mode == "Analyze One Stock" and st.button("Analyze Stock"):
    stock = get_stock_data(single_ticker)

    df = pd.DataFrame([
        {k: v for k, v in stock.items() if k != "History"}
    ])

    st.subheader("Stock Overview")
    st.dataframe(df, width="stretch")

    st.subheader("Market Signal")
    st.metric(label=f"{single_ticker} Signal", value=get_market_signal(stock))

    st.subheader("6-Month Price Trend")
    if not stock["History"].empty:
        st.line_chart(stock["History"]["Close"])

    st.subheader("Quick Watchlist Insight")
    if stock["Revenue Growth %"] != "N/A" and stock["Earnings Growth %"] != "N/A":
        if stock["Revenue Growth %"] > 15 and stock["Earnings Growth %"] > 15:
            st.success("This stock currently shows strong growth trends.")
        elif stock["Revenue Growth %"] > 0 and stock["Earnings Growth %"] > 0:
            st.info("This stock currently shows moderate positive growth.")
        else:
            st.warning("This stock has weaker or mixed recent growth trends.")
    else:
        st.info("Not enough financial trend data is available for a quick watchlist insight.")

    st.subheader("AI Deep Analysis")
    st.info("AI-generated analysis for educational purposes only. Not financial advice.")

    if "OPENAI_API_KEY" not in st.secrets:
        st.error("OPENAI_API_KEY is missing in Streamlit Secrets.")
    else:
        prompt = f"""
Analyze this stock for a beginner investor.

Company: {stock["Company"]}
Ticker: {stock["Ticker"]}
Price: {stock["Price"]}
Market Cap: {stock["Market Cap"]}
P/E Ratio: {stock["P/E Ratio"]}
Sector: {stock["Sector"]}
Revenue: {stock["Revenue"]}
Revenue Growth %: {stock["Revenue Growth %"]}
Net Income: {stock["Net Income"]}
Earnings Growth %: {stock["Earnings Growth %"]}
Gross Margin %: {stock["Gross Margin %"]}
Operating Margin %: {stock["Operating Margin %"]}
Market Signal: {get_market_signal(stock)}

Return your answer in this exact format:

## StockSnap AI Rating
- Rating: BUY, HOLD, or RISKY
- Overall Score: x/10
- Growth Score: x/10
- Valuation Score: x/10
- Profitability Score: x/10
- Risk Score: x/10
- Market Signal: {get_market_signal(stock)}

## What the Company Does
Give a simple 2-sentence explanation.

## Strengths
- 3 bullet points

## Risks
- 3 bullet points

## Beginner Summary
Give a short beginner-friendly summary.

Keep spacing clean and easy to read.
Not financial advice.
"""

        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt
            )
            st.markdown(response.output_text)
        except Exception as e:
            st.error(f"AI analysis could not load: {e}")