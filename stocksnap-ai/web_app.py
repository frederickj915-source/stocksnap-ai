import streamlit as st
import yfinance as yf
import pandas as pd
from openai import OpenAI

st.set_page_config(page_title="StockSnap AI", page_icon="📈", layout="wide")

st.title("📈 StockSnap AI")
st.write("Compare two stocks using real market and financial data.")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

ticker1 = st.text_input("Enter first stock ticker", value="NVDA").upper()
ticker2 = st.text_input("Enter second stock ticker", value="AMD").upper()


def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    income_stmt = stock.financials

    revenue = "N/A"
    net_income = "N/A"
    revenue_growth = "N/A"
    earnings_growth = "N/A"

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
        "History": hist
    }


if st.button("Analyze Stocks"):
    stock1 = get_stock_data(ticker1)
    stock2 = get_stock_data(ticker2)

    df = pd.DataFrame([
        {k: v for k, v in stock1.items() if k != "History"},
        {k: v for k, v in stock2.items() if k != "History"}
    ])

    st.subheader("Stock Comparison")
    st.dataframe(df, use_container_width=True)

    st.subheader("6-Month Price Trend")

    if not stock1["History"].empty:
        st.write(f"{ticker1} price chart")
        st.line_chart(stock1["History"]["Close"])

    if not stock2["History"].empty:
        st.write(f"{ticker2} price chart")
        st.line_chart(stock2["History"]["Close"])

    st.subheader("AI Summary")

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

Give:
- a simple comparison
- which stock looks stronger
- key risks for each
- a short beginner-friendly verdict

Keep it simple and not financial advice.
"""

    try:
        response = client.responses.create(
            model="gpt-5.4",
            input=prompt
        )
        st.write(response.output_text)
    except Exception as e:
        st.error(f"AI summary could not load: {e}")