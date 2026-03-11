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

mode = st.radio(
    "Choose analysis mode:",
    ["Compare Two Stocks", "Analyze One Stock"]
)

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

                revenue_growth = (
                    (revenue_series.iloc[0] - revenue_series.iloc[1])
                    / revenue_series.iloc[1]
                ) * 100

        if "Net Income" in income_stmt.index:

            income_series = income_stmt.loc["Net Income"]

            net_income = income_series.iloc[0]

            if len(income_series) > 1 and income_series.iloc[1] not in [0, None]:

                earnings_growth = (
                    (income_series.iloc[0] - income_series.iloc[1])
                    / income_series.iloc[1]
                ) * 100

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
        "History": hist,
    }


def get_market_signal(stock):

    score = 0

    if stock["Revenue Growth %"] != "N/A":
        if stock["Revenue Growth %"] > 20:
            score += 2
        elif stock["Revenue Growth %"] > 5:
            score += 1
        elif stock["Revenue Growth %"] < 0:
            score -= 1

    if stock["Earnings Growth %"] != "N/A":
        if stock["Earnings Growth %"] > 20:
            score += 2
        elif stock["Earnings Growth %"] > 5:
            score += 1
        elif stock["Earnings Growth %"] < 0:
            score -= 1

    if stock["P/E Ratio"] != "N/A":
        if stock["P/E Ratio"] < 25:
            score += 1
        elif stock["P/E Ratio"] > 60:
            score -= 1

    if stock["Gross Margin %"] != "N/A":
        if stock["Gross Margin %"] > 50:
            score += 1
        elif stock["Gross Margin %"] < 20:
            score -= 1

    if stock["Operating Margin %"] != "N/A":
        if stock["Operating Margin %"] > 20:
            score += 1
        elif stock["Operating Margin %"] < 5:
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
        {k: v for k, v in stock2.items() if k != "History"},
    ])

    st.subheader("Stock Comparison")
    st.dataframe(df, width="stretch")

    st.subheader("Market Signal")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(f"{ticker1} Signal", get_market_signal(stock1))

    with col2:
        st.metric(f"{ticker2} Signal", get_market_signal(stock2))

    st.subheader("6-Month Price Trend")

    if not stock1["History"].empty:
        st.line_chart(stock1["History"]["Close"])

    if not stock2["History"].empty:
        st.line_chart(stock2["History"]["Close"])

    st.subheader("AI Summary")

    if "OPENAI_API_KEY" not in st.secrets:
        st.error("OPENAI_API_KEY is missing in Streamlit Secrets.")
    else:

        prompt = f"""
Compare these two stocks for a beginner investor.

Stock 1:
{stock1}

Stock 2:
{stock2}

Explain which stock looks stronger and why.
"""

        try:

            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
            )

            st.markdown(response.output_text)

        except Exception as e:

            st.error(f"AI summary could not load: {e}")
