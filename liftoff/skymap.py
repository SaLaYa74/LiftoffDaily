"""Find-your-state sky maps (Jarvis, Nov 24 roundtable; owner: "Apply all").

Liftoff was flat (100-150 views a post) because it never used the formula that works on the other two pages:
everyone finds their own state on one screen, on the day people are talking about it. So on a big meteor shower's
peak night, every state is colored by tonight's cloud forecast.

Two independent forecasts, at each state's 2020 Census center of population (assets/cenpop2020_state.csv):
  - NWS National Digital Forecast Database sky cover (api.weather.gov gridpoints), hourly, % of sky covered
  - MET Norway Locationforecast cloud_area_fraction (api.met.no, ECMWF-based, CC BY 4.0: credit "MET Norway")
Each is averaged over the viewing window in the state's own time zone. A state is CLEAR only if BOTH say <= 30%,
CLOUDY only if BOTH say >= 70%, and a TOSS-UP otherwise (partly cloudy, or the two forecasts disagree). We never call
a state clear on one model's word.

Shapes: us-atlas 3.0.1 (ISC license, assets/us-atlas-LICENSE.txt), drawn by usmap.py.
"""
import csv
import os
import re
import time as _time
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, time, timedelta, timezone
from html import escape
from zoneinfo import ZoneInfo

from . import sources as S
from . import usmap as U

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
CLEAR_MAX, CLOUDY_MIN = 30, 70
CLEAR, TOSS, CLOUDY = "clear", "toss-up", "cloudy"
# (fill, label ink) on the dark night-sky look
COLORS = {CLEAR: ("#FFC94A", "#0B0F1A"), TOSS: ("#5B6B8C", "#FFFFFF"), CLOUDY: ("#262D3D", "#8A93A6")}
LEGEND = [(CLEAR, "Clear skies", "both forecasts ≤30% cloud"), (TOSS, "Toss-up", "partly cloudy or forecasts split"),
          (CLOUDY, "Clouded out", "both forecasts ≥70% cloud")]


def centers():
    """{fips: dict(abbr, name, lat, lon)} for the 50 states + DC (2020 Census centers of population)."""
    with open(os.path.join(ASSETS, "cenpop2020_state.csv")) as f:
        return {r["fips"]: {"abbr": r["abbr"], "name": r["name"], "lat": float(r["lat"]), "lon": float(r["lon"])}
                for r in csv.DictReader(f)}


def _get(url, ttl_min, tries=3):
    """api.weather.gov sometimes answers 500 for a moment; retry before giving up."""
    for k in range(tries):
        try:
            return S._fetch(url, ttl_min)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            if k == tries - 1:
                raise
            _time.sleep(2 + 3 * k)


def _span(valid):
    """'2026-12-14T03:00:00+00:00/PT3H' -> (start utc, hours)."""
    start, dur = valid.split("/")
    m = re.fullmatch(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?)?", dur)
    hours = int(m.group(1) or 0) * 24 + int(m.group(2) or 0) if m else 1
    return datetime.fromisoformat(start).astimezone(timezone.utc), max(1, hours)


def nws_sky(lat, lon):
    """NWS gridded sky cover: ({utc hour: %}, time zone name, update time)."""
    pt = _get(f"https://api.weather.gov/points/{lat:.4f},{lon:.4f}", 30 * 24 * 60)["properties"]
    grid = _get(pt["forecastGridData"], 45)["properties"]
    hours = {}
    for v in grid["skyCover"]["values"]:
        start, n = _span(v["validTime"])
        for h in range(n):
            hours[start + timedelta(hours=h)] = v["value"]
    return hours, pt["timeZone"], datetime.fromisoformat(grid["updateTime"]).astimezone(timezone.utc)


def met_sky(lat, lon):
    """MET Norway cloud area fraction: ({utc hour: %}, update time)."""
    d = _get(f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat:.4f}&lon={lon:.4f}", 45)
    hours = {datetime.fromisoformat(t["time"].replace("Z", "+00:00")): t["data"]["instant"]["details"].get("cloud_area_fraction")
             for t in d["properties"]["timeseries"]}
    return hours, datetime.fromisoformat(d["properties"]["meta"]["updated_at"].replace("Z", "+00:00"))


def window_hours(night, tz, start_h, end_h):
    """UTC hours from start_h local on `night` through end_h local the next morning (inclusive)."""
    z = ZoneInfo(tz)
    first = datetime.combine(night, time(start_h), tzinfo=z) if start_h >= 12 else \
        datetime.combine(night + timedelta(days=1), time(start_h), tzinfo=z)
    last = datetime.combine(night + timedelta(days=1), time(end_h), tzinfo=z)
    out, t = [], first
    while t <= last:
        out.append(t.astimezone(timezone.utc))
        t += timedelta(hours=1)
    return out


def verdict(nws, met):
    if nws <= CLEAR_MAX and met <= CLEAR_MAX:
        return CLEAR
    if nws >= CLOUDY_MIN and met >= CLOUDY_MIN:
        return CLOUDY
    return TOSS


def tonight(night, window, rep, now=None):
    """{fips: dict(abbr, name, nws, met, verdict)} for a viewing night, with every check on the Report."""
    now = now or datetime.now(timezone.utc)
    pts = centers()
    rep.require(len(pts) == 51, "skymap: 50 states + DC", f"{len(pts)} centers")

    def one(item):
        f, c = item
        try:
            nh, tz, nupd = nws_sky(c["lat"], c["lon"])
            mh, mupd = met_sky(c["lat"], c["lon"])
        except (urllib.error.URLError, KeyError, ValueError) as e:
            return f, None, f"{type(e).__name__}: {e}"
        return f, (nh, tz, nupd, mh, mupd), ""

    with ThreadPoolExecutor(6) as ex:
        got = list(ex.map(one, sorted(pts.items())))
    out, agree = {}, 0
    for f, data, err in got:
        c = pts[f]
        if not rep.require(data is not None, f"skymap: {c['abbr']} both forecasts loaded", err):
            continue
        nh, tz, nupd, mh, mupd = data
        hrs = window_hours(night, tz, *window)
        rep.require(now - nupd < timedelta(hours=24), f"skymap: {c['abbr']} NWS forecast is fresh", f"updated {nupd}")
        rep.require(now - mupd < timedelta(hours=24), f"skymap: {c['abbr']} MET Norway forecast is fresh", f"updated {mupd}")
        nv = [nh.get(h) for h in hrs]
        mv = [mh.get(h) for h in hrs]
        ok = all(v is not None and 0 <= v <= 100 for v in nv + mv)
        if not rep.require(ok, f"skymap: {c['abbr']} every hour of the window covered by both",
                           f"NWS {nv} / MET {mv} for {hrs[0]:%m-%d %H}-{hrs[-1]:%H} UTC"):
            continue
        n, m = sum(nv) / len(nv), sum(mv) / len(mv)
        v = verdict(n, m)
        agree += (n <= CLEAR_MAX) == (m <= CLEAR_MAX) and (n >= CLOUDY_MIN) == (m >= CLOUDY_MIN)
        out[f] = {**c, "nws": n, "met": m, "verdict": v, "tz": tz}
    rep.require(len(out) == 51, "skymap: a forecast for every state", f"{len(out)} of 51")
    # The models usually agree on the big picture; if they split on most states, something is off (or the night is
    # genuinely unpredictable): publish only when they agree on at least 60% of states.
    rep.require(agree >= 0.6 * max(1, len(out)), "skymap: the two forecasts mostly agree",
                f"agree on {agree} of {len(out)} states")
    return out


# ---------------------------------------------------------------- drawing

def map_svg(colors, labels, p=1.0, small_list=True, stroke="#0B0F1A"):
    """Dark-theme US map. colors: {fips: (fill, ink)}; labels: {fips: text in the state}. States fade in as p rises
    (west to east), so the map 'sweeps' like nightfall. Small Northeast states are listed off the Atlantic coast."""
    Sh = U.shapes()
    xs = [s["cx"] for s in Sh.values()]
    lo, hi = min(xs), max(xs)
    paths, texts = [], []
    op = lambda s: 1.0 if p >= 1 else max(0.0, min(1.0, (p - 0.55 * (s["cx"] - lo) / (hi - lo)) / 0.3))
    for f, s in Sh.items():
        fill, ink = colors[f]
        paths.append(f'<path d="{s["d"]}" fill="#141A28" stroke="{stroke}" stroke-width="1.6"/>'
                     f'<path d="{s["d"]}" fill="{fill}" opacity="{op(s):.2f}" stroke="{stroke}" stroke-width="1.6"/>')
        if f in U.SMALL or not labels.get(f):
            continue
        tiny = s["area"] < 1500
        x, y = (s["cx"] + 50, s["cy"] + 4) if tiny else (s["cx"], s["cy"])
        fs = 22 if tiny else max(15.0, min(24.0, 0.8 * s["w"] / (0.62 * max(len(labels[f]), 2))))
        ink = "#FFFFFF" if tiny else ink
        texts.append(f'<text x="{x:.1f}" y="{y + fs * 0.35:.1f}" text-anchor="middle" font-family="Space Grotesk" '
                     f'font-weight="700" font-size="{fs:.1f}" fill="{ink}" opacity="{op(s):.2f}">{escape(labels[f])}</text>')
    small = sorted((f for f in Sh if f in U.SMALL), key=lambda f: Sh[f]["cy"])
    for k, f in enumerate(small if small_list else ()):
        s = Sh[f]
        y = 150 + k * 40
        texts.append(f'<line x1="{s["cx"]:.1f}" y1="{s["cy"]:.1f}" x2="968" y2="{y - 7}" stroke="#5B6B8C" stroke-width="1.5"/>'
                     f'<rect x="970" y="{y - 22}" width="22" height="22" rx="5" fill="{colors[f][0]}" opacity="{max(op(s), .25):.2f}"/>'
                     f'<text x="999" y="{y - 4}" font-family="Space Grotesk" font-weight="700" font-size="22" fill="#FFFFFF" '
                     f'opacity="{op(s):.2f}">{escape(labels.get(f, ""))}</text>')
    return f'<svg viewBox="-6 -4 1122 622" style="width:100%;display:block">{"".join(paths)}{"".join(texts)}</svg>'


# ---------------------------------------------------------------- aurora: NOAA's own line, as a map (Nov 24)

# NOAA's storm watches say how far south the aurora may be seen, in words ("as low as New York to Wisconsin to
# Washington state"). We draw exactly that: the named states are NOAA's edge; a state is "north of the line" if its
# northern border (assets/state_bounds.csv, from us-atlas) reaches the line joining the named states (flat past the
# ends). Alaska is always in; Hawaii never is. If NOAA names no lower-48 state, there's no map.
AURORA = {"edge": ("#FFC94A", "#0B0F1A"), "in": ("#3DDC97", "#0B0F1A"), "out": ("#262D3D", "#8A93A6")}
AURORA_LEGEND = [("in", "Best chance", "north of NOAA's line"), ("edge", "NOAA's edge", "the states NOAA names"),
                 ("out", "Unlikely", "south of the line")]


def bounds():
    with open(os.path.join(ASSETS, "state_bounds.csv")) as f:
        return {r["fips"]: {k: float(r[k]) for k in ("min_lon", "min_lat", "max_lon", "max_lat")} for r in csv.DictReader(f)}


def named_states(text):
    """[(fips, 'northern'|'southern'|'')] for each state NOAA's sentence names, in order. Longest names first, and
    each match is blanked out, so 'West Virginia' never also counts as 'Virginia'."""
    found, t = [], text
    for f, c in sorted(centers().items(), key=lambda kv: -len(kv[1]["name"])):
        pat = r"\b((?:northern|southern)\s+)?" + re.escape(c["name"]) + r"\b"
        for m in re.finditer(pat, t, flags=re.I):
            found.append((m.start(), f, (m.group(1) or "").strip().lower()))
        t = re.sub(pat, lambda m: " " * len(m.group(0)), t, flags=re.I)
    return [(f, q) for _, f, q in sorted(found)]


def aurora_reach(text):
    """{fips: 'edge'|'in'|'out'} from NOAA's 'Aurora may be seen as low as ...' line, or None if it names no
    lower-48 state."""
    named = [(f, q) for f, q in named_states(text) if f not in ("02", "15")]
    if not named:
        return None
    b = bounds()
    cx = lambda f: (b[f]["min_lon"] + b[f]["max_lon"]) / 2

    def anchor(f, q):
        lo, hi = b[f]["min_lat"], b[f]["max_lat"]
        mid = (lo + hi) / 2
        return cx(f), {"northern": (mid + hi) / 2, "southern": (lo + mid) / 2}.get(q, mid)

    pts = sorted(anchor(f, q) for f, q in named)

    def line(lon):
        if lon <= pts[0][0]:
            return pts[0][1]
        if lon >= pts[-1][0]:
            return pts[-1][1]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 <= lon <= x1:
                return y0 + (y1 - y0) * (lon - x0) / ((x1 - x0) or 1)
        return pts[-1][1]

    edge = {f for f, _ in named}
    out = {}
    for f in b:
        if f in edge:
            out[f] = "edge"
        elif f == "02":
            out[f] = "in"
        elif f == "15":
            out[f] = "out"
        else:
            out[f] = "in" if b[f]["max_lat"] >= line(cx(f)) else "out"
    return out
