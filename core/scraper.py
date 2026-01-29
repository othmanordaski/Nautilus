"""Lobster-style scraper: provider selection, decrypt API, subtitles, quality."""
import re
import httpx
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
from models.media import MediaItem
from utils.config import config


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
        self.client = httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=15.0)

    async def close(self):
        await self.client.aclose()

    async def search(self, query: str) -> List[MediaItem]:
        slug = query.replace(" ", "-").lower().strip()
        if slug.startswith("-"):
            slug = slug[1:]
        url = f"{self.base_url}/search/{slug}"
        resp = await self.client.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
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

    async def get_seasons(self, media_id: str) -> List[Dict[str, Any]]:
        try:
            resp = await self.client.get(f"{self.base_url}/ajax/v2/tv/seasons/{media_id}")
            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.select(".dropdown-item[data-id]")
            return [
                {"id": el["data-id"], "number": i + 1, "label": el.get_text(strip=True) or f"Season {i + 1}"}
                for i, el in enumerate(items)
            ]
        except Exception:
            return []

    async def get_episodes(self, season_id: str) -> List[Dict[str, Any]]:
        try:
            resp = await self.client.get(f"{self.base_url}/ajax/v2/season/episodes/{season_id}")
            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.select(".nav-item a[data-id]")
            return [{"id": el["data-id"], "number": i + 1} for i, el in enumerate(items)]
        except Exception:
            return []

    def _pick_server_id(self, html: str) -> Optional[str]:
        """Parse servers page and return data-id for the configured provider (lobster: grep $provider)."""
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.select("a[data-id][title]"):
            if self.provider.lower() in (a.get("title") or "").lower():
                return a.get("data-id")
        # Fallback: first server
        first = soup.select_one("a[data-id]")
        return first["data-id"] if first else None

    async def _get_embed_link(self, episode_id: str) -> Optional[str]:
        """Get embed URL from ajax/episode/sources/{episode_id}."""
        try:
            resp = await self.client.get(f"{self.base_url}/ajax/episode/sources/{episode_id}")
            return resp.json().get("link")
        except Exception:
            return None

    async def _extract_from_embed(self, embed_url: str) -> Dict[str, Any]:
        """Lobster extract_from_embed: call decrypt API, get video + subs. Returns dict with file, subs, full json."""
        out = {"file": None, "subs": [], "json": None}
        try:
            dec = await self.client.get(f"{self.decrypt_api}/?url={embed_url}")
            data = dec.json()
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
        except Exception:
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
                # Movie: ajax/movie/episodes -> pick link with provider title -> get episode id from href
                resp = await self.client.get(f"{self.base_url}/ajax/movie/episodes/{media.id}")
                soup = BeautifulSoup(resp.text, "html.parser")
                episode_id = None
                for a in soup.select("a[data-link][title]"):
                    if self.provider.lower() in (a.get("title") or "").lower():
                        href = a.get("href") or a.get("data-link") or ""
                        # lobster: episode_id from URL like ...-123.456 -> 456
                        m = re.search(r"-(\d+)\.(\d+)(?:\?|$)", href)
                        if m:
                            episode_id = m.group(2)
                        break
                if not episode_id:
                    first = soup.select_one("a[data-link]")
                    if first:
                        href = first.get("href") or first.get("data-link") or ""
                        m = re.search(r"-(\d+)\.(\d+)(?:\?|$)", href)
                        if m:
                            episode_id = m.group(2)
                if not episode_id:
                    return None
                display_title = media.title
            else:
                if not episode_server_id:
                    return None
                # TV: episode/servers page -> pick server by provider -> get sources
                srv_resp = await self.client.get(f"{self.base_url}/ajax/v2/episode/servers/{episode_server_id}")
                server_id = self._pick_server_id(srv_resp.text)
                if not server_id:
                    return None
                src_resp = await self.client.get(f"{self.base_url}/ajax/episode/sources/{server_id}")
                embed_url = src_resp.json().get("link") if src_resp.json() else None
                if not embed_url:
                    return None
                display_title = f"{media.title} - S{season_num}E{episode_num}"
                ext = await self._extract_from_embed(embed_url)
                url = ext.get("file")
                if not url:
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
                return None
            ext = await self._extract_from_embed(embed_url)
            url = ext.get("file")
            if not url:
                return None
            url = self._apply_quality(url)
            subs = [] if config.get("no_subs") else (ext.get("subs") or [])
            return {
                "url": url,
                "title": display_title,
                "subs_links": subs,
                "json_data": ext.get("json"),
            }
        except Exception:
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
