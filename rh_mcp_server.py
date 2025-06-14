#from kusto_tool import run_kusto_query
import datetime, uuid,logging, json
from mcp.server.fastmcp import FastMCP
import logging
import robin_stocks.robinhood as r
from dotenv import load_dotenv
import os, json, logging
import yfinance as yf

load_dotenv(override=True)  # Load environment variables from .env file

# This is the shared MCP server instance
robinhood_mcp = FastMCP("rh-mcp-server")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("rh-mcp-server")
logger.info("Initializing Robinhood MCP server...")

    
def map_stock_price_to_symbol(positions_data: list) -> dict:
    """
    Maps stock prices to their respective symbols.
    """
    stocks_in_account = [stock['symbol'] for stock in positions_data] #Get all stocks in account
    price_of_stock = r.get_latest_price(stocks_in_account) #get prices of those stock
    #create a map of stock: price
    stock_prices = {}
    for i in range(len(stocks_in_account)):
        stock_prices[stocks_in_account[i]] = price_of_stock[i]
    return stock_prices


def login_to_robinhood() -> None:
    """
    Login to Robinhood using credentials from environment variables.
    """
    #if not userid or not password:
    # If no credentials are provided, try to get them from environment variables
    userid = os.getenv("rh_login_id")
    password = os.getenv("rh_login_password")
    login = r.login(userid, password)
    
@robinhood_mcp.resource("stock://{symbol}")
def stock_resource(symbol: str) -> str:
    """
    Expose stock price data as a resource.
    Returns a formatted string with the current stock price for the given symbol.
    """
    logger.info("stock_resource")
    price = get_stock_price(symbol)
    if price < 0:
        return f"Error: Could not retrieve price for symbol '{symbol}'."
    return f"The current price of '{symbol}' is ${price:.2f}."

@robinhood_mcp.tool()
def get_stock_history(symbol: str, period: str = "1mo") -> str:
    """
    Retrieve historical data for a stock given a ticker symbol and a period.
    Returns the historical data as a CSV formatted string.
    
    Parameters:
        symbol: The stock ticker symbol.
        period: The period over which to retrieve historical data (e.g., '1mo', '3mo', '1y').
    """
    logger.info(f"Tool called : get_stock_history {symbol} {period}")
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        if data.empty:
            return f"No historical data found for symbol '{symbol}' with period '{period}'."
        # Convert the DataFrame to a CSV formatted string
        csv_data = data.to_csv()
        return csv_data
    except Exception as e:
        return f"Error fetching historical data: {str(e)}"

@robinhood_mcp.tool()
def compare_stocks(symbol1: str, symbol2: str) -> str:
    """
    Compare the current stock prices of two ticker symbols.
    Returns a formatted message comparing the two stock prices.
    
    Parameters:
        symbol1: The first stock ticker symbol.
        symbol2: The second stock ticker symbol.
    """
    logger.info(f"Tool called : compare_stocks {symbol1} {symbol2}")
    price1 = get_stock_price(symbol1)
    price2 = get_stock_price(symbol2)
    if price1 < 0 or price2 < 0:
        return f"Error: Could not retrieve data for comparison of '{symbol1}' and '{symbol2}'."
    if price1 > price2:
        result = f"{symbol1} (${price1:.2f}) is higher than {symbol2} (${price2:.2f})."
    elif price1 < price2:
        result = f"{symbol1} (${price1:.2f}) is lower than {symbol2} (${price2:.2f})."
    else:
        result = f"Both {symbol1} and {symbol2} have the same price (${price1:.2f})."
    return result

@robinhood_mcp.tool()
def get_stock_price(symbol: str) -> str:
    """
    Retrieve the current stock price for the given ticker symbol.
    Returns the latest closing price as a float.
    """
    logger.info(f"Tool called : get_stock_price {symbol}")
    try:
        ticker = yf.Ticker(symbol)
        # Get today's historical data; may return empty if market is closed or symbol is invalid.
        data = ticker.history(period="1d")
        if not data.empty:
            # Use the last closing price from today's data
            price = data['Close'].iloc[-1]
            return float(price)
        else:
            # As a fallback, try using the regular market price from the ticker info
            info = ticker.info
            price = info.get("regularMarketPrice", None)
            if price is not None:
                return float(price)
            else:
                return -1.0  # Indicate failure
    except Exception:
        # Return -1.0 to indicate an error occurred when fetching the stock price
        return -1.0


@robinhood_mcp.tool()
def get_robinhood_portfolio() -> list:
    """
    Get details of user's Robinhood portfolio.
    Retrieves the user's open stock positions, including symbol, shares, average buy price, quantity,

    """
    login_to_robinhood()  # Ensure we are logged in before fetching data
    positions_data = r.get_open_stock_positions()    
    stock_prices = map_stock_price_to_symbol(positions_data)

    stocks = []
    for item in positions_data:
        #print(item)
        stock = {}
        stock['symbol'] = item['symbol']
        stock['shares'] = item['shares_available_for_exercise']
        stock['average_buy_price'] = item['average_buy_price']
        stock['quantity'] = item['quantity']
        stock['price_paid'] = item['clearing_cost_basis']
        stock['current_value'] =  float(stock['shares']) * float(stock_prices[stock['symbol']])
        stocks.append(stock)
        
    return stocks

if __name__ == "__main__":
    print("Starting Review MCP server using logger...")
    #stocks = get_robinhood_portfolio()
    #print("Robinhood Portfolio:", json.dumps(stocks, indent=2))
    robinhood_mcp.run()