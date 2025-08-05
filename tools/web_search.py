import os
from googleapiclient.discovery import build

def web_search_tool(query: str) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")

    if not api_key or not cse_id:
        return "Missing API key or CSE ID for web search."

    try:
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=query, cx=cse_id, num=3).execute()
        results = res.get("items", [])
        
        if not results:
            return "No search results found."

        output = ""
        for i, item in enumerate(results, 1):
            output += f"\nResult {i}:\n{item.get('title')}\n{item.get('snippet')}\n{item.get('link')}\n"
        return output.strip()

    except Exception as e:
        return f"Web search error: {e}"

# Useful for experimenting directly
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    print(web_search_tool("Apple 2022 EBITDA"))