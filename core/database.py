"""History storage: lobster-style full state (position, TV season/episode) for continue & next episode."""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Any
from utils.config import config


class Database:
    def __init__(self):
        path = config.get("history_db") or "nautilus.db"
        if not path.startswith("/") and not path.startswith(".") and ":" not in path[:2]:
            path = str(Path(__file__).parent.parent / path)
        self.conn = sqlite3.connect(path)
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='history'")
        if cur.fetchone():
            cur = self.conn.execute("PRAGMA table_info(history)")
            cols = [r[1] for r in cur.fetchall()]
            if "position" not in cols:
                self.conn.execute("ALTER TABLE history RENAME TO history_old")
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                media_id TEXT NOT NULL,
                title TEXT,
                media_type TEXT,
                position TEXT,
                season_id TEXT NOT NULL DEFAULT '',
                episode_id TEXT NOT NULL DEFAULT '',
                season_title TEXT,
                episode_title TEXT,
                data_id TEXT,
                image_link TEXT,
                updated DATETIME,
                PRIMARY KEY (media_id, season_id, episode_id)
            )
        """)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_history_updated ON history(updated DESC)")
        cur = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='history_old'")
        if cur.fetchone():
            self.conn.execute("""
                INSERT OR IGNORE INTO history (media_id, title, media_type, position, season_id, episode_id, updated)
                SELECT id, title, media_type, '00:00:00', '', '', datetime('now') FROM history_old
            """)
            self.conn.execute("DROP TABLE history_old")
        self.conn.commit()

    def log_view(self, media_id: str, title: str, m_type: str, **kwargs):
        """Simple log (backward compat). For full state use save_history."""
        position = kwargs.get("position", "00:00:00")
        season_id = kwargs.get("season_id") or ""
        episode_id = kwargs.get("episode_id") or ""
        season_title = kwargs.get("season_title") or ""
        episode_title = kwargs.get("episode_title") or ""
        data_id = kwargs.get("data_id") or ""
        image_link = kwargs.get("image_link") or ""
        now = datetime.now()
        self.conn.execute(
            """INSERT OR REPLACE INTO history
               (media_id, title, media_type, position, season_id, episode_id,
                season_title, episode_title, data_id, image_link, updated)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (media_id, title, m_type, position, season_id, episode_id,
             season_title, episode_title, data_id, image_link, now),
        )
        self.conn.commit()

    def save_history(
        self,
        media_id: str,
        title: str,
        media_type: str,
        position: str = "00:00:00",
        season_id: Optional[str] = None,
        episode_id: Optional[str] = None,
        season_title: Optional[str] = None,
        episode_title: Optional[str] = None,
        data_id: Optional[str] = None,
        image_link: Optional[str] = None,
    ):
        """Lobster-style: save full state for continue and next episode."""
        self.log_view(
            media_id, title, media_type,
            position=position, season_id=season_id or "", episode_id=episode_id or "",
            season_title=season_title or "", episode_title=episode_title or "",
            data_id=data_id or "", image_link=image_link or "",
        )

    def get_recent(self, limit: int = 3):
        """Last N titles (simple)."""
        return self.conn.execute(
            "SELECT DISTINCT title FROM history ORDER BY updated DESC LIMIT ?", (limit,)
        ).fetchall()

    def get_history_list(self, limit: int = 50) -> List[dict]:
        """Full rows for continue menu: most recent first, one row per watch state."""
        rows = self.conn.execute(
            """SELECT media_id, title, media_type, position, season_id, episode_id,
                      season_title, episode_title, data_id, image_link
               FROM history ORDER BY updated DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [
            {
                "media_id": r[0], "title": r[1], "media_type": r[2], "position": r[3],
                "season_id": r[4], "episode_id": r[5], "season_title": r[6],
                "episode_title": r[7], "data_id": r[8], "image_link": r[9],
            }
            for r in rows
        ]

    def get_entry(self, media_id: str, season_id: Optional[str] = None, episode_id: Optional[str] = None) -> Optional[dict]:
        """Get one history entry by media_id and optionally season/episode (for TV)."""
        if season_id and episode_id:
            row = self.conn.execute(
                """SELECT media_id, title, media_type, position, season_id, episode_id,
                          season_title, episode_title, data_id, image_link
                   FROM history WHERE media_id = ? AND season_id = ? AND episode_id = ?""",
                (media_id, season_id, episode_id),
            ).fetchone()
        else:
            row = self.conn.execute(
                """SELECT media_id, title, media_type, position, season_id, episode_id,
                          season_title, episode_title, data_id, image_link
                   FROM history WHERE media_id = ? AND (season_id IS NULL OR season_id = '') LIMIT 1""",
                (media_id,),
            ).fetchone()
        if not row:
            return None
        return {
            "media_id": row[0], "title": row[1], "media_type": row[2], "position": row[3],
            "season_id": row[4], "episode_id": row[5], "season_title": row[6],
            "episode_title": row[7], "data_id": row[8], "image_link": row[9],
        }

    def delete_media(self, media_id: str):
        """Remove all history for a media (e.g. when finished)."""
        self.conn.execute("DELETE FROM history WHERE media_id = ?", (media_id,))
        self.conn.commit()
