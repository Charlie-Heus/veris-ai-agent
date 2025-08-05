# tools/sec_search.py
import finnhub
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("FINNHUB_API_KEY")

# Set up the Finnhub client
client = finnhub.Client(api_key=api_key)

import finnhub
import os
from dotenv import load_dotenv
import re

load_dotenv()

finnhub_api_key = os.getenv("FINNHUB_API_KEY")
client = finnhub.Client(api_key=finnhub_api_key)

def sec_search_tool(query: str) -> str:
    """
    Example query: "AAPL EBITDA 2022"
    """
    try:
        # Parse the query
        parts = query.strip().split()
        if len(parts) < 3:
            return "Error: Query should be like 'AAPL EBITDA 2022'"

        symbol, metric, year = parts[0], parts[1].upper(), parts[2]

        # Fetch fundamentals
        fundamentals = client.company_basic_financials(symbol, 'all')

        if "metric" not in fundamentals or not fundamentals["metric"]:
            return f"No financial data found for {symbol}."

        # Look for the closest year-based value (e.g., trailing metrics)
        if metric in fundamentals["metric"]:
            value = fundamentals["metric"][metric]
            return f"{symbol} {metric} in {year}: {value}"
        else:
            # Try to display known available metrics
            known = ', '.join(fundamentals["metric"].keys())
            return f"Metric '{metric}' not found. Available: {known}"
    
    except finnhub.FinnhubAPIException as e:
        return f"API error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
    

if __name__ == "__main__":
    query = input("Enter query (e.g. 'AAPL EBITDA 2022'): ")
    print(sec_search_tool(query))
    print()