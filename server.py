from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
import os
import requests
from dice_roller import DiceRoller

load_dotenv()

mcp = FastMCP("mcp-server")
client = TavilyClient(os.getenv("TAVILY_API_KEY"))

@mcp.tool()
def web_search(query: str) -> str:
    """Search the web for information about the given query"""
    search_results = client.get_search_context(query=query)
    return search_results

@mcp.tool()
def roll_dice(notation: str, num_rolls: int = 1) -> str:
    """Roll the dice with the given notation"""
    roller = DiceRoller(notation, num_rolls)
    return str(roller)

"""
Add your own tool here, and then use it through Cursor!
"""
@mcp.tool()
def number_fact(query: str) -> str:
    """Get an interesting fact about a number or date using NumbersAPI."""
    try:
        # You can pass things like "42", "math/42", or "date/6/14"
        url = f"http://numbersapi.com/{query}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return f"⚠️ API error: {response.status_code}"
    except Exception as e:
        return f"❌ Something went wrong: {e}"


@mcp.tool()
def space_fact() -> str:
    """Get NASA's Astronomy Picture of the Day (APOD) with its title, date, description, and image URL."""
    try:
        api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")  # fallback if not set
        url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            title = data.get("title", "Unknown Title")
            explanation = data.get("explanation", "No description available.")
            date = data.get("date", "")
            image_url = data.get("hdurl") or data.get("url")  # sometimes only 'url' exists

            message = (
                f"🪐 **{title}** ({date})\n\n"
                f"{explanation}\n\n"
                f"📸 Image URL: {image_url}"
            )
            return message
        else:
            return f"⚠️ NASA API error: {response.status_code}"
    except Exception as e:
        return f"❌ Something went wrong: {e}"
        
@mcp.tool()
def animal_fact(animal: str = "dog") -> str:
    """Get a fun fact about a given animal."""
    try:
        url = f"https://some-random-api.com/facts/{animal.lower()}"
        r = requests.get(url)
        if r.status_code == 200:
            return r.json().get("fact", "No fact found.")
        return f"⚠️ API error: {r.status_code}"
    except Exception as e:
        return f"❌ Something went wrong: {e}"

@mcp.tool()
def science_term(term: str) -> str:
    """Explain a science term using Wikipedia summaries."""
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{term}"
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            return f"🔬 {data.get('extract', 'No summary found.')}"
        return f"⚠️ Wikipedia error: {r.status_code}"
    except Exception as e:
        return f"❌ Something went wrong: {e}"        
        
if __name__ == "__main__":
    mcp.run(transport="stdio")