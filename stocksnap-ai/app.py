import yfinance as yf

ticker1 = input("Enter first stock ticker: ").upper()
ticker2 = input("Enter second stock ticker: ").upper()

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info

    company = info.get("longName", "N/A")
    price = info.get("currentPrice", "N/A")
    market_cap = info.get("marketCap", "N/A")
    pe_ratio = info.get("trailingPE", "N/A")

    income_stmt = stock.financials

    revenue = "N/A"
    net_income = "N/A"

    if not income_stmt.empty:
        if "Total Revenue" in income_stmt.index:
            revenue = income_stmt.loc["Total Revenue"].iloc[0]

        if "Net Income" in income_stmt.index:
            net_income = income_stmt.loc["Net Income"].iloc[0]

    return {
        "company": company,
        "price": price,
        "market_cap": market_cap,
        "pe_ratio": pe_ratio,
        "revenue": revenue,
        "net_income": net_income
    }

stock1 = get_stock_data(ticker1)
stock2 = get_stock_data(ticker2)

print("\nSTOCK COMPARISON\n")

print("Company 1:", stock1["company"])
print("Price:", stock1["price"])
print("Market Cap:", stock1["market_cap"])
print("P/E Ratio:", stock1["pe_ratio"])
print("Revenue:", stock1["revenue"])
print("Net Income:", stock1["net_income"])

print("\n-----------------------\n")

print("Company 2:", stock2["company"])
print("Price:", stock2["price"])
print("Market Cap:", stock2["market_cap"])
print("P/E Ratio:", stock2["pe_ratio"])
print("Revenue:", stock2["revenue"])
print("Net Income:", stock2["net_income"])