from pathlib import Path
from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache
from langchain_community.cache import SQLiteCache

MEMORY_CACHE = InMemoryCache()
def configure_cache(mode: str):
    if mode == 'Memory':
        set_llm_cache(MEMORY_CACHE)
    elif mode == 'SQLite':
        folder = Path('.cache')
        folder.mkdir(exist_ok=True)
        set_llm_cache(SQLiteCache(database_path=str(folder/'langchain.db')))
    else:
        set_llm_cache(None)
