from dataclasses import dataclass
from typing import Optional

@dataclass
class MediaItem:
    title: str
    id: str
    type: str  # 'movie' or 'tv'
    url: str
    stream_url: Optional[str] = None

    def __str__(self):
        return f"{self.title} ({self.type.upper()})"