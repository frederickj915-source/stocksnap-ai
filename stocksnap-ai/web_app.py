import streamlit as st
import yfinance as yf
import pandas as pd
from openai import OpenAI


st.set_page_config(page_title="StockSnap AI", layout="wide")

st.title("StockSnap AI")
st.write("Compare two stocks in simple beginner-friendly language.")


@st.cache_data(ttl=600)
def get_stock_data(ticker: str) -> dict:
    stock = yf.Ticker(ticker)

    # Price history
    try:
        history = stock.history(period="6mo")
    except Exception:
        history = pd.DataFrame()

    # Basic info
    try:
        info = stock.info
    except Exception:
        info = {}

    revenue = info.get("totalRevenue", "N/A")
    net_income = info.get("netIncomeToCommon", "N/A")
    gross_margin = info.get("grossMargins", "N/A")
    operating_margin = info.get("operatingMargins", "N/A")
    revenue_growth = info.get("revenueGrowth", "N/A")
    earnings_growth = info.get("earningsGrowth", "N/A")
    current_price = info.get("currentPrice", "N/A")
    market_cap = info.get("marketCap", "N/A")
    pe_ratio = info.get("trailingPE", "N/A")
    forward_pe = info.get("forwardPE", "N/A")

    return {
        "Ticker": ticker.upper(),
        "History": history,
        "Info": info,
        "Revenue": revenue,
        "Net Income": net_income,
        "Gross Margin": gross_margin,
        "Operating Margin": operating_margin,
        "Revenue Growth": revenue_growth,
        "Earnings Growth": earnings_growth,
        "Current Price": current_price,
        "Market Cap": market_cap,
        "PE Ratio": pe_ratio,
        "Forward PE": forward_pe,
    }


def format_value(value):
    if value in [None, "", "N/A"]:
        return "N/A"

    if isinstance(value, (int, float)):
        # Percent-like values from yfinance often come as decimals
        if -1 < value < 1 and value != 0:
            return f"{value:.2%}"

        abs_value = abs(value)
        if abs_value >= 1_000_000_000_000:
            return f"${value / 1_000_000_000_000:.2f}T"
        if abs_value >= 1_000_000_000:
            return f"${value / 1_000_000_000:.2f}B"
        if abs_value >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"
        if abs_value >= 1_000:
            return f"${value / 1_000:.2f}K"

        return f"{value:.2f}"

    return str(value)


ticker1 = st.text_input("Enter first stock ticker", placeholder="AAPL")
ticker2 = st.text_input("Enter second stock ticker", placeholder="MSFT")

analyze = st.button("Analyze Stocks")

if analyze:
    if not ticker1 or not ticker2:
        st.warning("Please enter two stock tickers.")
        st.stop()

    try:
        data1 = get_stock_data(ticker1.strip().upper())
        data2 = get_stock_data(ticker2.strip().upper())
    except Exception as e:
        st.error(f"Could not load stock data: {e}")
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"{data1['Ticker']} Snapshot")
        st.write(f"**Current Price:** {format_value(data1['Current Price'])}")
        st.write(f"**Market Cap:** {format_value(data1['Market Cap'])}")
        st.write(f"**Revenue:** {format_value(data1['Revenue'])}")
        st.write(f"**Net Income:** {format_value(data1['Net Income'])}")
        st.write(f"**Revenue Growth:** {format_value(data1['Revenue Growth'])}")
        st.write(f"**Earnings Growth:** {format_value(data1['Earnings Growth'])}")
        st.write(f"**Gross Margin:** {format_value(data1['Gross Margin'])}")
        st.write(f"**Operating Margin:** {format_value(data1['Operating Margin'])}")
        st.write(f"**P/E Ratio:** {format_value(data1['PE Ratio'])}")
        st.write(f"**Forward P/E:** {format_value(data1['Forward PE'])}")

    with col2:
        st.subheader(f"{data2['Ticker']} Snapshot")
        st.write(f"**Current Price:** {format_value(data2['Current Price'])}")
        st.write(f"**Market Cap:** {format_value(data2['Market Cap'])}")
        st.write(f"**Revenue:** {format_value(data2['Revenue'])}")
        st.write(f"**Net Income:** {format_value(data2['Net Income'])}")
        st.write(f"**Revenue Growth:** {format_value(data2['Revenue Growth'])}")
        st.write(f"**Earnings Growth:** {format_value(data2['Earnings Growth'])}")
        st.write(f"**Gross Margin:** {format_value(data2['Gross Margin'])}")
        st.write(f"**Operating Margin:** {format_value(data2['Operating Margin'])}")
        st.write(f"**P/E Ratio:** {format_value(data2['PE Ratio'])}")
        st.write(f"**Forward P/E:** {format_value(data2['Forward PE'])}")

    st.subheader("6-Month Price Trend")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        if not data1["History"].empty and "Close" in data1["History"]:
            st.write(f"**{data1['Ticker']}**")
            st.line_chart(data1["History"]["Close"])
        else:
            st.info(f"No chart data available for {data1['Ticker']}.")

    with chart_col2:
        if not data2["History"].empty and "Close" in data2["History"]:
            st.write(f"**{data2['Ticker']}**")
            st.line_chart(data2["History"]["Close"])
        else:
            st.info(f"No chart data available for {data2['Ticker']}.")

    st.subheader("AI Summary")

    if "OPENAI_API_KEY" not in st.secrets:
        st.error("OPENAI_API_KEY is missing in Streamlit Secrets.")
    else:
        rev1 = format_value(data1["Revenue"])
        net1 = format_value(data1["Net Income"])
        growth1 = format_value(data1["Revenue Growth"])
        earn_growth1 = format_value(data1["Earnings Growth"])
        gross1 = format_value(data1["Gross Margin"])
        op1 = format_value(data1["Operating Margin"])
        price1 = format_value(data1["Current Price"])
        cap1 = format_value(data1["Market Cap"])
        pe1 = format_value(data1["PE Ratio"])
        fpe1 = format_value(data1["Forward PE"])

        rev2 = format_value(data2["Revenue"])
        net2 = format_value(data2["Net Income"])
        growth2 = format_value(data2["Revenue Growth"])
        earn_growth2 = format_value(data2["Earnings Growth"])
        gross2 = format_value(data2["Gross Margin"])
        op2 = format_value(data2["Operating Margin"])
        price2 = format_value(data2["Current Price"])
        cap2 = format_value(data2["Market Cap"])
        pe2 = format_value(data2["PE Ratio"])
        fpe2 = format_value(data2["Forward PE"])

        prompt = f"""
Compare these two stocks for a beginner investor.

Stock 1: {data1["Ticker"]}
Current Price: {price1}
Market Cap: {cap1}
Revenue: {rev1}
Net Income: {net1}
Revenue Growth: {growth1}
Earnings Growth: {earn_growth1}
Gross Margin: {gross1}
Operating Margin: {op1}
P/E Ratio: {pe1}
Forward P/E: {fpe1}

Stock 2: {data2["Ticker"]}
Current Price: {price2}
Market Cap: {cap2}
Revenue: {rev2}
Net Income: {net2}
Revenue Growth: {growth2}
Earnings Growth: {earn_growth2}
Gross Margin: {gross2}
Operating Margin: {op2}
P/E Ratio: {pe2}
Forward P/E: {fpe2}

Return your answer in this format:

## Which Stock Looks Stronger
Say which stock currently looks stronger for a beginner investor and why.

## Key Strengths
List the biggest strengths of each stock.

## Risks
Mention the main risks for each stock.

## Beginner Takeaway
Give a simple explanation a beginner investor could understand.

Keep it concise. Do not ask follow-up questions.
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
