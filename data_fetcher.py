import yfinance as yf
import pprint

ticker = "RELIANCE.NS"
stock = yf.Ticker(ticker)

def get_fundamentals(stock):
    data = stock.info
    return {
        # --- Valuation ---
        "current_price": data.get("currentPrice"),          # Current trading price in INR
        "market_cap": data.get("marketCap"),                # Total market value of the company
        "trailing_pe": data.get("trailingPE"),              # Price/Earnings based on past 12 months
        "forward_pe": data.get("forwardPE"),                # Price/Earnings based on future estimates
        "peg_ratio": data.get("pegRatio"),                  # PE adjusted for growth rate
        "price_to_book": data.get("priceToBook"),           # Market price vs book value

        # --- Profitability ---
        "trailing_eps": data.get("trailingEps"),            # Earnings per share (last 12 months)
        "forward_eps": data.get("forwardEps"),              # Earnings per share (estimated)
        "return_on_equity": data.get("returnOnEquity"),     # Profit generated per rupee of equity
        "return_on_assets": data.get("returnOnAssets"),     # How efficiently assets generate profit
        "profit_margins": data.get("profitMargins"),        # Net profit as % of revenue
        "operating_margins": data.get("operatingMargins"),  # Operating profit as % of revenue

        # --- Growth ---
        "revenue_growth": data.get("revenueGrowth"),        # YoY revenue growth rate
        "earnings_growth": data.get("earningsGrowth"),      # YoY earnings growth rate
        "revenue_per_share": data.get("revenuePerShare"),   # Revenue divided by total shares

        # --- Financial Health ---
        "total_debt": data.get("totalDebt"),                # Total debt the company owes
        "debt_to_equity": data.get("debtToEquity"),         # Debt vs shareholder equity ratio
        "free_cashflow": data.get("freeCashflow"),          # Cash left after capital expenditures
        "current_ratio": data.get("currentRatio"),          # Ability to pay short term liabilities
        "quick_ratio": data.get("quickRatio"),              # Stricter short term liquidity measure

        # --- Dividends & Risk ---
        "dividend_yield": data.get("dividendYield"),        # Annual dividend as % of stock price
        "payout_ratio": data.get("payoutRatio"),            # % of earnings paid as dividends
        "beta": data.get("beta"),                           # Volatility vs market (1 = same as market)

        # --- 52 Week Range ---
        "52w_high": data.get("fiftyTwoWeekHigh"),           # Highest price in last 52 weeks
        "52w_low": data.get("fiftyTwoWeekLow"),             # Lowest price in last 52 weeks
        "50d_avg": data.get("fiftyDayAverage"),             # Average price over last 50 days
        "200d_avg": data.get("twoHundredDayAverage"),       # Average price over last 200 days

        # --- Company Info ---
        "name": data.get("longName"),                       # Full company name
        "sector": data.get("sector"),                       # Business sector eg. Energy, IT
        "industry": data.get("industry"),                   # Specific industry within sector
        "country": data.get("country"),                     # Country of incorporation
    }
    
    
def financials_to_text(stock):
    income = stock.financials.to_string()
    balance = stock.balance_sheet.to_string()
    cashflow = stock.cashflow.to_string()
    
    return f"INCOME STATEMENT:\n{income}\n\nBALANCE SHEET:\n{balance}\n\nCASH FLOW:\n{cashflow}"


def get_news(stock):
    res = []
    for Stock in stock.news:
       title = Stock['content']['title']
       summary = Stock['content']['summary']
       res.append({"title": title, "summary": summary})
    return res

#pprint.pp(get_news(stock))

