"""Liftoff Daily look: real photo underneath, huge condensed claim on top, one accent color.
Overlays render on a transparent background; video.py lays them over the moving photo."""
from html import escape

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Anton&family=Space+Grotesk:wght@500;700&display=block" rel="stylesheet">')

ACCENT = "#FFC94A"      # warm "sunlit" gold: pops on dark skies without fighting the photo
BASE_CSS = """*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;background:transparent;overflow:hidden;-webkit-font-smoothing:antialiased}
body{font-family:"Space Grotesk",Arial,sans-serif;color:#fff}
.claim{font-family:Anton,Impact,sans-serif;text-transform:uppercase;line-height:.98;letter-spacing:1px;
       text-shadow:0 4px 28px rgba(0,0,0,.65),0 2px 4px rgba(0,0,0,.6)}
.hl{color:%s}
.box{position:absolute;left:70px;right:70px}
.sub{font-weight:700;font-size:50px;line-height:1.18;text-shadow:0 3px 18px rgba(0,0,0,.8)}
.chip{display:inline-block;font-weight:700;font-size:34px;letter-spacing:3px;text-transform:uppercase;color:#0B0F1A;
      background:%s;padding:10px 22px;border-radius:12px;margin-bottom:26px}
""" % (ACCENT, ACCENT)


# Text block position per layout. "low" also keeps clear of the Like/Comment/Share column on the right.
TOP = {"high": {"hook": 260, "stat": 300, "line": 300, "rows": 250, "send": 640},
       "low": {"hook": 900, "stat": 860, "line": 960, "rows": 820, "send": 960}}
RIGHT = {"high": 70, "low": 170}


def _at(kind, layout):
    return f"top:{TOP[layout][kind]}px;right:{RIGHT[layout]}px"


def _page(body, extra_css=""):
    return f"<!doctype html><html><head><meta charset='utf-8'>{FONTS}<style>{BASE_CSS}{extra_css}</style></head><body>{body}</body></html>"


def mark(text):
    """*word* → accent color. Everything else is escaped."""
    parts = escape(text).split("*")
    # accent phrases never break across lines ("6 / WEEKS" reads badly)
    return "".join(f'<span class="hl">{p.replace(" ", "&nbsp;")}</span>' if i % 2 else p for i, p in enumerate(parts))


GRADIENT = {
    "high": "linear-gradient(180deg,rgba(4,6,14,.78) 0%,rgba(4,6,14,.25) 34%,rgba(4,6,14,0) 50%,rgba(4,6,14,.35) 70%,rgba(4,6,14,.85) 100%)",
    "low": "linear-gradient(180deg,rgba(4,6,14,.45) 0%,rgba(4,6,14,0) 22%,rgba(4,6,14,0) 38%,rgba(4,6,14,.55) 52%,rgba(4,6,14,.6) 78%,rgba(4,6,14,.85) 100%)",
}


def frame_layer(handle, credit, layout="high"):
    """Constant layer: legibility gradients, handle, photo credit. Kept inside Instagram's safe zones."""
    return _page(f"""
<div style="position:absolute;inset:0;background:{GRADIENT[layout]}"></div>
<div style="position:absolute;left:70px;top:150px;font-weight:700;font-size:30px;letter-spacing:4px;opacity:.9">
  🚀 {escape(handle.upper())}</div>
<div style="position:absolute;left:70px;bottom:250px;font-size:24px;opacity:.75">{escape(credit)}</div>""")


def hook(big, small="", chip="", layout="high"):
    """Beat 1: the bold claim. `big` supports *accent* words; `small` is a supporting line."""
    chip_html = f'<div class="chip">{escape(chip)}</div>' if chip else ""
    small_html = f'<div class="sub" style="margin-top:34px">{mark(small)}</div>' if small else ""
    size = 150 if len(big) <= 34 else (128 if len(big) <= 52 else 108)
    return _page(f'<div class="box" style="{_at("hook", layout)}">{chip_html}<div class="claim" style="font-size:{size}px">'
                 f'{mark(big)}</div>{small_html}</div>')


def stat(number, label, note="", layout="high"):
    """A huge number with a label: '150' / 'shooting stars an hour'."""
    note_html = f'<div class="sub" style="font-size:40px;opacity:.9;margin-top:22px">{mark(note)}</div>' if note else ""
    return _page(f'<div class="box" style="{_at("stat", layout)}"><div class="claim hl" style="font-size:330px;line-height:.9">'
                 f'{escape(number)}</div><div class="claim" style="font-size:92px;margin-top:10px">{mark(label)}</div>'
                 f'{note_html}</div>')


def line(text, sub="", chip="", layout="high"):
    """A mid-video beat: one strong line, optional detail."""
    chip_html = f'<div class="chip">{escape(chip)}</div>' if chip else ""
    sub_html = f'<div class="sub" style="margin-top:28px">{mark(sub)}</div>' if sub else ""
    size = 120 if len(text) <= 30 else 100
    return _page(f'<div class="box" style="{_at("line", layout)}">{chip_html}<div class="claim" style="font-size:{size}px">'
                 f'{mark(text)}</div>{sub_html}</div>')


def rows(title, items, chip="", layout="high"):
    """A short list: [(left, right), ...] e.g. launches this week."""
    chip_html = f'<div class="chip">{escape(chip)}</div>' if chip else ""
    body = "".join(
        f'<div style="display:flex;gap:26px;align-items:baseline;padding:22px 0;border-top:2px solid rgba(255,255,255,.18)">'
        f'<div class="claim hl" style="font-size:54px;min-width:190px">{escape(a)}</div>'
        f'<div class="sub" style="font-size:42px">{mark(b)}</div></div>' for a, b in items)
    return _page(f'<div class="box" style="{_at("rows", layout)}">{chip_html}<div class="claim" style="font-size:104px;margin-bottom:26px">'
                 f'{mark(title)}</div>{body}</div>')


def send(text, sub="", layout="high"):
    """Last beat: the send prompt."""
    sub_html = f'<div class="sub" style="margin-top:26px;opacity:.9">{mark(sub)}</div>' if sub else ""
    align = "center" if layout == "high" else "left"
    return _page(f'<div class="box" style="{_at("send", layout)};text-align:{align}"><div class="claim" style="font-size:112px">'
                 f'{mark(text)}</div>{sub_html}</div>')
