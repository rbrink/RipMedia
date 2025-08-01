import requests
from io import BytesIO
from tkinter import messagebox
from PIL import Image

from config import Config
from utils import Logger
from modules.api.omdb_cache import OMDBCache

class omdb_api:
    def __init__(self):
        self.omdb_cache = OMDBCache()
        self.logger = Logger.get_logger(__name__)

    def query_omdb(self, title):
        """Query OMDB API for movie/series information."""
        cache_key = f"query:{title}"
        cached = self.omdb_cache.get(cache_key)
        if cached:
            self.logger.debug(f"OMDB cache hit for {title}")
            return cached
        
        params = {
            "apikey": Config.get('OMDB API Key'),
            "t": title
        }
        try:
            response = requests.get("http://www.omdbapi.com/", params=params)
            data = response.json()
            if data.get("Response") == "True":
                result = {
                    "Title": data.get("Title"),
                    "Type": data.get("Type"),    # movie or series
                    "Year": data.get("Year"),
                    "Rated": data.get("Rated"),
                    "Runtime": data.get("Runtime"),
                    "Genre": data.get("Genre"),
                    "Poster": data.get("Poster"),
                    "Plot": data.get("Plot"),
                    "IMDB": data.get("imdbID")
                }
                self.omdb_cache.set(cache_key, result)
                return result
            else:
                self.logger.error(f"OMDB Error: {data.get("Error")}")
                return None
        except Exception as e:
            self.logger.error(f"OMDB query failed: {e}")
            messagebox.showerror("OMDB query failed", f"{e}")
            return None

    def fetch_poster(self, poster_url):
        try:
            response = requests.get(poster_url)
            img_data = BytesIO(response.content)
            return Image.open(img_data)
        except Exception as e:
            self.logger.error(f"Failed to fetch poster: {e}")
            messagebox.showerror("Error", f"Failed to fetch poster:\n{e}")
            return None

    def search_omdb(self, query):
        cache_key = f"search:{query}"
        cached = self.omdb_cache.get(cache_key)
        if cached:
            self.logger.debug(f"OMDB search cache hit for {query}")
            return cached
        
        url = f"http://www.omdbapi.com/?apikey={Config.get('OMDB API Key')}&s={query}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data.get("Response") == "True":
                results = data.get("Search", [])
                self.omdb_cache.set(cache_key, results)
                return results
        except Exception as e:
            self.logger.error(f"OMDb search failed: {e}")
            messagebox.showerror("Error", f"OMDB search failed:\n{e}")
        return []
