"""Pre-publish checks.

Every post carries a Report. A single BLOCK result stops the post from publishing;
WARN results are published but surfaced in the run summary. The full report is
saved next to the post's media (checks.json) as an audit trail.
"""
import json
import os
import re

from PIL import Image, ImageStat

PASS, WARN, BLOCK = "pass", "warn", "block"

# Hype is fine; claims we can't stand behind are not.
BANNED_WORDS = ("confirmed alien", "aliens confirmed", "end of the world", "doomsday", "will hit earth",
                "nasa confirms", "nasa warns", "100% visible", "guaranteed", "100% guaranteed")

# Image credits we're allowed to publish (public domain or CC BY with credit). Anything else blocks.
ALLOWED_CREDITS = ("NASA", "ESA/Webb", "ESA/Hubble", "NOAA", "USGS", "JPL", "Liftoff Daily")


class Report:
    def __init__(self, subject=""):
        self.subject = subject
        self.items = []

    def add(self, status, name, detail=""):
        self.items.append({"status": status, "check": name, "detail": str(detail)})
        return status == PASS

    def require(self, ok, name, detail=""):
        """BLOCK when ok is False."""
        return self.add(PASS if ok else BLOCK, name, "" if ok else detail)

    def expect(self, ok, name, detail=""):
        """WARN when ok is False."""
        return self.add(PASS if ok else WARN, name, "" if ok else detail)

    def extend(self, other):
        self.items.extend(other.items)
        return self

    @property
    def blocked(self):
        return [i for i in self.items if i["status"] == BLOCK]

    @property
    def warnings(self):
        return [i for i in self.items if i["status"] == WARN]

    @property
    def ok(self):
        return not self.blocked

    def counts(self):
        return {s: sum(i["status"] == s for i in self.items) for s in (PASS, WARN, BLOCK)}

    def markdown(self):
        c = self.counts()
        lines = [f"**Checks:** ✅ {c[PASS]} passed · ⚠️ {c[WARN]} warnings · ⛔ {c[BLOCK]} blocking"]
        for i in self.blocked + self.warnings:
            icon = "⛔" if i["status"] == BLOCK else "⚠️"
            lines.append(f"- {icon} {i['check']}: {i['detail']}")
        return "\n".join(lines)

    def save(self, path):
        with open(path, "w") as f:
            json.dump({"subject": self.subject, "counts": self.counts(), "checks": self.items}, f, indent=2)


# ---------------- reusable checks ----------------

def image(rep, path, size):
    expected = {"feed": (1080, 1350), "story": (1080, 1920), "reel": (1080, 1920), "square": (1080, 1080)}[size]
    name = os.path.basename(path)
    if not rep.require(os.path.exists(path), f"{name}: rendered", "file missing"):
        return
    im = Image.open(path)
    rep.require(im.size == expected, f"{name}: dimensions", f"{im.size} != {expected}")
    rep.require(os.path.getsize(path) > 30_000, f"{name}: not empty", f"only {os.path.getsize(path)} bytes")
    spread = max(ImageStat.Stat(im.convert("L")).stddev)
    rep.require(spread > 12, f"{name}: has visible content", f"image looks blank (contrast {spread:.1f})")


def credit(rep, text):
    """Every photo we show must come from a source we're allowed to publish, and be credited."""
    ok = any(text.startswith(c) or f" {c}" in text or f"({c}" in text for c in ALLOWED_CREDITS)
    rep.require(bool(text) and ok, "image: rights-clean credit", f"credit {text!r} is not public domain / CC BY")


def caption(rep, text):
    rep.require(0 < len(text) <= 2200, "caption: length", f"{len(text)} chars (max 2200)")
    rep.require(text.count("#") <= 5, "caption: 5 hashtags max", f"{text.count('#')} hashtags")
    rep.require("source:" in text.lower(), "caption: cites its source", "no 'Source:' line")
    rep.require("photo:" in text.lower() or "image:" in text.lower() or "graphic:" in text.lower(),
                "caption: credits the visual", "no 'Photo:' / 'Image:' / 'Graphic:' credit")
    low = text.lower()
    bad = [w for w in BANNED_WORDS if re.search(r"(?<![\w'])" + re.escape(w) + r"(?![\w'])", low)]
    rep.require(not bad, "caption: brand language", f"contains {bad}")
    rep.require("None" not in text and "nan" not in low.split(), "caption: no missing values", "caption contains None/nan")


def agree(rep, name, a, b, tol, unit=""):
    """Two independent sources must agree within tol."""
    ok = a is not None and b is not None and abs(a - b) <= tol
    return rep.require(ok, f"{name}: two sources agree", f"{a}{unit} vs {b}{unit} (tolerance {tol}{unit})")
