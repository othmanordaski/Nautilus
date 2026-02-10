"""Lobster-style scraper: provider selection, decrypt API, subtitles, quality."""
import re
import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
from models.media import MediaItem
from utils.config import config
from rich.console import Console

# Use lxml for faster parsing if available, otherwise fall back to html.parser
try:
    import lxml  # noqa: F401
    _HTML_PARSER = "lxml"
except Exception:
    _HTML_PARSER = "html.parser"

console = Console()


class FlixScraper:
    def __init__(self):
        base = (config.get("base_url") or "https://flixhq.to").strip()
        if not base.startswith("http"):
            base = "https://" + base
        self.base_url = base
        self.decrypt_api = config.get("decrypt_api")
        self.provider = (config.get("provider") or "Vidcloud").strip()
        self.subs_language = (config.get("subs_language") or "english").strip().lower()
        if self.subs_language.startswith("."):
            self.subs_language = self.subs_language[1:]
        headers = {"User-Agent": config.get("user_agent")}
        self.client = httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0)
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds

    async def _request_with_retry(self, method: str, url: str, **kwargs) -> Optional[httpx.Response]:
        """Execute HTTP request with exponential backoff retry logic."""
        for attempt in range(self.max_retries):
            try:
                if method == "GET":
                    response = await self.client.get(url, **kwargs)
                elif method == "POST":
                    response = await self.client.post(url, **kwargs)
                else:
                    response = await self.client.request(method, url, **kwargs)
                
                response.raise_for_status()
                return response
                
            except httpx.TimeoutException:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    console.print(f"[#d29922]Request timeout. Retrying in {delay:.1f}s... ({attempt + 1}/{self.max_retries})[/#d29922]")
                    await asyncio.sleep(delay)
                else:
                    console.print(f"[#f85149]Request timed out after {self.max_retries} attempts[/#f85149]")
                    return None
                    
            except httpx.HTTPStatusError as e:
                if attempt < self.max_retries - 1 and e.response.status_code >= 500:
                    delay = self.retry_delay * (2 ** attempt)
                    console.print(f"[#d29922]Server error ({e.response.status_code}). Retrying in {delay:.1f}s... ({attempt + 1}/{self.max_retries})[/#d29922]")
                    await asyncio.sleep(delay)
                else:
                    console.print(f"[#f85149]HTTP error {e.response.status_code}: {e.response.reason_phrase}[/#f85149]")
                    return None
                    
            except httpx.NetworkError:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    console.print(f"[#d29922]Network error. Retrying in {delay:.1f}s... ({attempt + 1}/{self.max_retries})[/#d29922]")
                    await asyncio.sleep(delay)
                else:
                    console.print(f"[#f85149]Network error: Unable to connect after {self.max_retries} attempts[/#f85149]")
                    return None
                    
            except Exception as e:
                console.print(f"[#f85149]Unexpected error: {type(e).__name__}: {e}[/#f85149]")
                return None
        
        return None

    async def close(self):
        await self.client.aclose()

    async def search(self, query: str) -> List[MediaItem]:
        slug = query.replace(" ", "-").lower().strip()
        if slug.startswith("-"):
            slug = slug[1:]
        url = f"{self.base_url}/search/{slug}"
        
        resp = await self._request_with_retry("GET", url)
        if not resp:
            return []
        
        try:
            soup = BeautifulSoup(resp.text, _HTML_PARSER)
            results = []
            for item in soup.select(".flw-item"):
                link = item.select_one(".film-name a")
                if not link:
                    continue
                href = link.get("href", "")
                title = link.get_text(strip=True)
                mid = href.split("-")[-1] if "-" in href else ""
                kind = "tv" if "/tv/" in href else "movie"
                results.append(MediaItem(title=title, id=mid, type=kind, url=href))
            return results
        except Exception as e:
            console.print(f"[#f85149]Failed to parse search results: {e}[/#f85149]")
            return []

    async def get_seasons(self, media_id: str) -> List[Dict[str, Any]]:
        try:
            resp = await self._request_with_retry("GET", f"{self.base_url}/ajax/v2/tv/seasons/{media_id}")
            if not resp:
                return []
            
            soup = BeautifulSoup(resp.text, _HTML_PARSER)
            items = soup.select(".dropdown-item[data-id]")
            return [
                {"id": el["data-id"], "number": i + 1, "label": el.get_text(strip=True) or f"Season {i + 1}"}
                for i, el in enumerate(items)
            ]
        except Exception as e:
            console.print(f"[#f85149]Failed to load seasons: {e}[/#f85149]")
            return []

    async def get_episodes(self, season_id: str) -> List[Dict[str, Any]]:
        try:
            resp = await self._request_with_retry("GET", f"{self.base_url}/ajax/v2/season/episodes/{season_id}")
            if not resp:
                return []
            
            soup = BeautifulSoup(resp.text, _HTML_PARSER)
            items = soup.select(".nav-item a[data-id]")
            return [{"id": el["data-id"], "number": i + 1} for i, el in enumerate(items)]
        except Exception as e:
            console.print(f"[#f85149]Failed to load episodes: {e}[/#f85149]")
            return []

    def _pick_server_id(self, html: str) -> Optional[str]:
        """Parse servers page and return data-id for the configured provider (lobster: grep $provider)."""
        soup = BeautifulSoup(html, _HTML_PARSER)
        for a in soup.select("a[data-id][title]"):
            if self.provider.lower() in (a.get("title") or "").lower():
                return a.get("data-id")
        # Fallback: first server
        first = soup.select_one("a[data-id]")
        return first["data-id"] if first else None

    async def _get_embed_link(self, episode_id: str) -> Optional[str]:
        """Get embed URL from ajax/episode/sources/{episode_id}."""
        try:
            resp = await self._request_with_retry("GET", f"{self.base_url}/ajax/episode/sources/{episode_id}")
            if not resp:
                return None
            return resp.json().get("link")
        except Exception as e:
            console.print(f"[#f85149]Failed to get embed link: {e}[/#f85149]")
            return None

    async def _extract_from_embed(self, embed_url: str) -> Dict[str, Any]:
        """Lobster extract_from_embed: call decrypt API, get video + subs. Returns dict with file, subs, full json."""
        out = {"file": None, "subs": [], "json": None}
        try:
            resp = await self._request_with_retry("GET", f"{self.decrypt_api}/?url={embed_url}")
            if not resp:
                return out
            
            data = resp.json()
            out["json"] = data
            sources = data.get("sources") or []
            if sources:
                out["file"] = sources[0].get("file")
            # Subtitles: lobster uses "label" containing subs_language
            tracks = data.get("tracks") or []
            for t in tracks:
                label = (t.get("label") or "").lower()
                if self.subs_language in label and t.get("file"):
                    out["subs"].append(t["file"])
            return out
        except Exception as e:
            console.print(f"[#f85149]Failed to decrypt stream: {e}[/#f85149]")
            return out

    def _apply_quality(self, url: str) -> str:
        """Lobster: replace /playlist.m3u8 with /$quality/index.m3u8."""
        if not url:
            return url
        q = config.get("quality") or "1080"
        return re.sub(r"/playlist\.m3u8\b", f"/{q}/index.m3u8", url, flags=re.I)

    async def get_stream_data(
        self,
        media: MediaItem,
        episode_server_id: Optional[str] = None,
        season_num: Optional[int] = None,
        episode_num: Optional[int] = None,
        is_movie: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Lobster-style: resolve embed -> decrypt -> video URL + subtitles.
        For TV pass episode_server_id (data_id). For movie we resolve from media.id.
        Returns: { url, title, subs_links, json_data } (url has quality applied).
        """
        try:
            if is_movie:
                # Movie: ajax/movie/episodes -> pick link with provider title -> extract episode_id from href
                resp = await self._request_with_retry("GET", f"{self.base_url}/ajax/movie/episodes/{media.id}")
                if not resp:
                    return None
                
                # Parse HTML to find server link matching provider
                html = resp.text
                # Remove newlines and split by class="nav-item" like lobster does
                html = html.replace('\n', '')
                parts = html.split('class="nav-item"')
                
                episode_id = None
                for part in parts[1:]:  # Skip first part before any nav-item
                    # Look for href and title in this nav-item
                    # Pattern: href="..." ... title="Provider"
                    title_match = re.search(r'title="([^"]*)"', part)
                    if title_match and self.provider.lower() in title_match.group(1).lower():
                        # Found matching provider, extract href
                        href_match = re.search(r'href="([^"]*)"', part)
                        if href_match:
                            href = href_match.group(1)
                            # Extract episode_id from URL format: /watch-movie-name-{movie_id}.{episode_id}
                            id_match = re.search(r'-(\d+)\.(\d+)$', href)
                            if id_match:
                                episode_id = id_match.group(2)
                                break
                
                if not episode_id:
                    console.print(f"[#f85149]Could not find episode ID for {media.title}[/#f85149]")
                    return None
                display_title = media.title
            else:
                if not episode_server_id:
                    return None
                # TV: episode/servers page -> pick server by provider -> get sources
                srv_resp = await self._request_with_retry("GET", f"{self.base_url}/ajax/v2/episode/servers/{episode_server_id}")
                if not srv_resp:
                    return None
                
                server_id = self._pick_server_id(srv_resp.text)
                if not server_id:
                    console.print(f"[#f85149]Could not find server for provider: {self.provider}[/#f85149]")
                    return None
                
                src_resp = await self._request_with_retry("GET", f"{self.base_url}/ajax/episode/sources/{server_id}")
                if not src_resp:
                    return None
                
                embed_url = src_resp.json().get("link") if src_resp.json() else None
                if not embed_url:
                    console.print(f"[#f85149]Could not get embed URL[/#f85149]")
                    return None
                display_title = f"{media.title} - S{season_num}E{episode_num}"
                ext = await self._extract_from_embed(embed_url)
                url = ext.get("file")
                if not url:
                    console.print(f"[#f85149]Failed to extract video URL[/#f85149]")
                    return None
                url = self._apply_quality(url)
                subs = [] if config.get("no_subs") else ext.get("subs") or []
                return {
                    "url": url,
                    "title": display_title,
                    "subs_links": subs,
                    "json_data": ext.get("json"),
                }
            # Movie path: get embed from episode_id
            embed_url = await self._get_embed_link(episode_id)
            if not embed_url:
                console.print(f"[#f85149]Could not get embed link for {media.title}[/#f85149]")
                return None
            ext = await self._extract_from_embed(embed_url)
            url = ext.get("file")
            if not url:
                console.print(f"[#f85149]Failed to extract video URL for {media.title}[/#f85149]")
                return None
            url = self._apply_quality(url)
            subs = [] if config.get("no_subs") else (ext.get("subs") or [])
            return {
                "url": url,
                "title": display_title,
                "subs_links": subs,
                "json_data": ext.get("json"),
            }
        except Exception as e:
            console.print(f"[#f85149]Error getting stream data: {type(e).__name__}: {e}[/#f85149]")
            return None

    async def get_stream_url(self, media: MediaItem, s: int = 1, e: int = 1) -> Optional[Dict]:
        """Backward compat: returns {url, title} (no subs). For full data use get_stream_data."""
        if media.type == "movie":
            data = await self.get_stream_data(media, is_movie=True)
        else:
            s_list = await self.get_seasons(media.id)
            if s < 1 or s > len(s_list):
                return None
            season_id = s_list[s - 1]["id"]
            e_list = await self.get_episodes(season_id)
            if e < 1 or e > len(e_list):
                return None
            ep = e_list[e - 1]
            data = await self.get_stream_data(
                media, episode_server_id=ep["id"], season_num=s, episode_num=ep["number"]
            )
        if not data:
            return None
        return {"url": data["url"], "title": data["title"]}

    async def get_stream_url_for_episode(
        self,
        media: MediaItem,
        episode_id: str,
        season_num: int,
        episode_num: int,
    ) -> Optional[Dict[str, Any]]:
        """Full stream data for one episode (for PLAY flow: url + subs)."""
        return await self.get_stream_data(
            media,
            episode_server_id=episode_id,
            season_num=season_num,
            episode_num=episode_num,
        )

    async def get_movie_stream_data(self, media: MediaItem) -> Optional[Dict[str, Any]]:
        """Full stream data for movie."""
        return await self.get_stream_data(media, is_movie=True)

    async def get_episode_server_id_by_provider(self, data_id: str) -> Optional[str]:
        """Given episode servers page data_id, return server id for configured provider (for next episode)."""
        resp = await self.client.get(f"{self.base_url}/ajax/v2/episode/servers/{data_id}")
        return self._pick_server_id(resp.text)
