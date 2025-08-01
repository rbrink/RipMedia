import requests
from tkinter import messagebox
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from utils import Logger
from modules.api.tvmaze_cache import TVMazeCache

class TVMazeAPI:
    BASE_URL = "https://api.tvmaze.com"

    def __init__(self):
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.tvmaze_cache = TVMazeCache()
        self.logger = Logger.get_logger(__name__)

    def search_show(self, query):
        cache_key = f"search:{query}"
        cached = self.tvmaze_cache.get(cache_key)
        if cached:
            self.logger.debug(f"TVMaze search cache hit for {query}")
            return cached
        
        url = f"{self.BASE_URL}/search/shows?q={query}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            result = response.json()
            self.tvmaze_cache.set(cache_key, result)
            return result
        except requests.RequestException as e:
            self.logger.error(f"TVMaze search failed: {e}")
            messagebox.showerror("Error", f"TVMaze search failed:\n{e}")
            return []

    def get_show_details(self, show_id):
        cache_key = f"show:{show_id}"
        cached = self.tvmaze_cache.get(cache_key)
        if cached:
            self.logger.debug(f"TVMaze show cache hit for {show_id}")
            return cached
        
        url = f"{self.BASE_URL}/shows/{show_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            result = response.json()
            self.tvmaze_cache.set(cache_key, result)
            return result
        except requests.RequestException as e:
            self.logger.error(f"TVMaze show details fetch failed: {e}")
            messagebox.showerror("Error", f"TVMaze show detailes fetch failed:\n{e}")
            return None
        
    def get_seasons(self, show_id):
        url = f"https://api.tvmaze.com/shows/{show_id}/seasons"
        response = requests.get(url)
        if response.status_code == 200:
           return response.json()
        return []

    def get_episodes(self, show_id, season=None):
        cache_key = f"episodes:{show_id}:{season}"
        cached = self.tvmaze_cache.get(cache_key)
        if cached:
            self.logger.debug(f"TVMaze episodes cache hit for {show_id}:{season}")
            return cached
        
        url = f"{self.BASE_URL}/shows/{show_id}/episodes"
        response = self.session.get(url)
        response.raise_for_status()
        all_episodes = response.json()
        filtered = [ep for ep in all_episodes if ep['season'] == season]
        for ep in filtered:
            ep['runtime_seconds'] = (ep.get('runtime') or 42) * 60  # Default to 42 minutes if runtime is not available
        self.tvmaze_cache.set(cache_key, filtered)
        return filtered
