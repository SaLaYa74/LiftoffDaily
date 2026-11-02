"""Shared post plumbing."""
from dataclasses import dataclass, field

from . import checks as C

MAX_CAROUSEL = 10


class DataError(Exception):
    """Data failed checks or isn't ready; nothing is posted."""


class NoContent(DataError):
    """Nothing to post right now (no event due, already covered). Skipped quietly."""


@dataclass
class Post:
    key: str
    caption: str
    images: list = field(default_factory=list)
    media: str = "feed"
    checks: C.Report = field(default_factory=C.Report)

    @property
    def size(self):
        return {"story": "story", "reel": "reel"}.get(self.media, "feed")
