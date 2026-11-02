"""Space data feeds. All free, no sign-up. Responses are cached on disk for a short time so a run
never hammers a source (Launch Library 2 allows ~15 calls an hour).

Network trouble raises urllib.error.URLError, which the runner treats as "try again later".
"""
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "data", "cache")
UA = "LiftoffDaily/1.0 (Instagram @liftoff_daily; contact via GitHub SaLaYa74)"
AU_KM = 149_597_870.7
LD_KM = 384_400            # one average Earth-Moon distance ("lunar distance")


def _fetch(url, ttl_min, raw=False, timeout=60):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, hashlib.sha1(url.encode()).hexdigest()[:16] + (".bin" if raw else ".json"))
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < ttl_min * 60:
        with open(path, "rb") as f:
            body = f.read()
    else:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
        with open(path, "wb") as f:
            f.write(body)
    return body if raw else json.loads(body)


def _utc(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc) if s else None


# ---------------------------------------------------------------- launches

def launches(limit=30, search=None):
    """Upcoming launches from The Space Devs Launch Library 2, soonest first."""
    q = {"limit": limit, "mode": "normal"}
    if search:
        q["search"] = search
    d = _fetch("https://ll.thespacedevs.com/2.3.0/launches/upcoming/?" + urllib.parse.urlencode(q), ttl_min=30)
    out = []
    for r in d.get("results", []):
        rocket = ((r.get("rocket") or {}).get("configuration") or {})
        mission = r.get("mission") or {}
        pad = r.get("pad") or {}
        out.append({
            "id": r["id"], "name": r["name"], "net": _utc(r.get("net")),
            "precision": ((r.get("net_precision") or {}).get("name") or "Unknown"),
            "status": ((r.get("status") or {}).get("abbrev") or "?"),
            "provider": ((r.get("launch_service_provider") or {}).get("name") or ""),
            "rocket": rocket.get("full_name") or rocket.get("name") or "",
            "mission": mission.get("name") or "", "mission_type": mission.get("type") or "",
            "description": mission.get("description") or "",
            "orbit": ((mission.get("orbit") or {}).get("name") or ""),
            "pad": pad.get("name") or "", "location": ((pad.get("location") or {}).get("name") or ""),
            "country": ((pad.get("country") or {}).get("alpha_2_code") or ""),
        })
    return out


def launches_rll():
    """Second, independent launch schedule (RocketLaunch.live free feed: next 5 launches)."""
    d = _fetch("https://fdo.rocketlaunch.live/json/launches/next/5", ttl_min=30)
    return [{"t0": _utc(r.get("t0") or r.get("win_open")), "provider": r["provider"]["name"],
             "vehicle": r["vehicle"]["name"], "name": r["name"]} for r in d.get("result", [])]


PROVIDER_ALIASES = {"china aerospace science and technology corporation": "casc", "united launch alliance": "ula",
                    "agency for defense development": "add", "japan aerospace exploration agency": "jaxa",
                    "indian space research organization": "isro", "russian federal space agency (roscosmos)": "roscosmos"}


def rll_match(launch, rll, hours=2):
    """The RocketLaunch.live entry that agrees with an LL2 launch on provider and time, if any."""
    first = lambda s: (PROVIDER_ALIASES.get(s.lower().strip(), s.lower()).split() or [""])[0]
    for r in rll:
        if r["t0"] and launch["net"] and abs((r["t0"] - launch["net"]).total_seconds()) <= hours * 3600 \
                and first(r["provider"]) == first(launch["provider"]):
            return r
    return None


# ---------------------------------------------------------------- Moon and sky

def moon_phases(start, count=8):
    """Primary moon phases from the US Naval Observatory: [(utc datetime, 'Full Moon'), ...]."""
    d = _fetch(f"https://aa.usno.navy.mil/api/moon/phases/date?date={start:%Y-%m-%d}&nump={count}", ttl_min=24 * 60)
    return [(datetime(p["year"], p["month"], p["day"], *map(int, p["time"].split(":")), tzinfo=timezone.utc),
             p["phase"]) for p in d["phasedata"]]


def moon_day(day, lat=39.0, lon=-95.0, tz_name="America/Chicago"):
    """USNO's Moon for one local date at a reference spot (default: middle of the US).
    Returns {'phase': 'Waxing Crescent', 'lit': 19, 'rise': time|None, 'set': time|None}."""
    from zoneinfo import ZoneInfo
    off = datetime.combine(day, datetime.min.time(), tzinfo=ZoneInfo(tz_name)).utcoffset().total_seconds() / 3600
    d = _fetch(f"https://aa.usno.navy.mil/api/rstt/oneday?date={day:%Y-%m-%d}&coords={lat},{lon}&tz={off:g}",
               ttl_min=24 * 60)["properties"]["data"]
    times = {m["phen"]: datetime.strptime(m["time"][:5], "%H:%M").time() for m in d.get("moondata", [])}
    return {"phase": d.get("curphase", ""), "lit": int(str(d.get("fracillum", "0")).rstrip("%") or 0),
            "rise": times.get("Rise"), "set": times.get("Set")}


def moon_distance_km(when):
    """Earth-Moon center distance at a UTC time, from JPL Horizons."""
    t0 = when.astimezone(timezone.utc)
    q = {"format": "json", "COMMAND": "'301'", "CENTER": "'500@399'", "EPHEM_TYPE": "OBSERVER",
         "START_TIME": f"'{t0:%Y-%m-%d %H:%M}'", "STOP_TIME": f"'{t0 + timedelta(minutes=1):%Y-%m-%d %H:%M}'",
         "STEP_SIZE": "'1m'", "QUANTITIES": "'20'"}
    r = _fetch("https://ssd.jpl.nasa.gov/api/horizons.api?" + urllib.parse.urlencode(q), ttl_min=7 * 24 * 60)["result"]
    row = r[r.index("$$SOE") + 5:r.index("$$EOE")].strip().splitlines()[0].split()
    return float(row[2]) * AU_KM


# ---------------------------------------------------------------- aurora / space weather

def kp_forecast():
    """NOAA SWPC planetary K-index, observed + 3-day forecast: [(utc datetime, kp, 'observed'|'predicted'), ...]."""
    d = _fetch("https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json", ttl_min=20)
    if d and isinstance(d[0], list):                     # older list-of-lists format
        d = [dict(zip(d[0], row)) for row in d[1:]]
    return [(_utc(r["time_tag"] + "Z" if not r["time_tag"].endswith("Z") else r["time_tag"]), float(r["kp"]),
             r.get("observed")) for r in d]


def storm_watch(msg):
    """Parse a SWPC geomagnetic storm watch: {'levels': {date: G-level int}, 'aurora': "Aurora may be seen..."}."""
    levels = {}
    lines = msg.splitlines()
    for i, l in enumerate(lines):
        if l.startswith("Highest Storm Level Predicted by Day"):
            for mon, day, g in re.findall(r"([A-Z][a-z]{2}) (\d{2}):\s+(?:G(\d)|None)", lines[i + 1]):
                levels[(mon, int(day))] = int(g or 0)
    aurora = next((l.split("Aurora - ", 1)[1].strip() for l in lines if l.startswith("Aurora - ")), "")
    return {"levels": levels, "aurora": aurora}


def swpc_messages(code_prefix="WATA"):
    """Official SWPC alerts/watches/warnings (WATA = geomagnetic storm watch, ALTK = K-index alert)."""
    d = _fetch("https://services.swpc.noaa.gov/products/alerts.json", ttl_min=20)
    out = []
    for a in d:
        msg = a.get("message", "").replace("\r", "")
        code = msg.split("Space Weather Message Code:")[-1].split()[0] if "Message Code:" in msg else ""
        if code.startswith(code_prefix):
            out.append({"issued": _utc(a["issue_datetime"].replace(" ", "T") + "Z"), "code": code, "message": msg})
    return out


# ---------------------------------------------------------------- asteroids

def close_approaches(days=30, max_ld=5):
    """Asteroid close approaches from JPL CNEOS, closest first."""
    q = {"date-min": "now", "date-max": f"+{days}", "dist-max": f"{max_ld}LD", "sort": "dist", "diameter": "true"}
    d = _fetch("https://ssd-api.jpl.nasa.gov/cad.api?" + urllib.parse.urlencode(q), ttl_min=6 * 60)
    f = d.get("fields", [])
    return [dict(zip(f, row)) for row in d.get("data", [])]


# ---------------------------------------------------------------- news and trends

def news(limit=40):
    """Latest space headlines (Spaceflight News API: NASA, ESA, SpaceNews, NASASpaceflight, ...)."""
    d = _fetch(f"https://api.spaceflightnewsapi.net/v4/articles/?limit={limit}", ttl_min=30)
    return [{"title": a["title"], "site": a["news_site"], "url": a["url"], "summary": a.get("summary", ""),
             "published": _utc(a["published_at"])} for a in d["results"]]


def pageviews(article, days=14):
    """Daily English Wikipedia views for an article: the trend radar (never shown as a fact)."""
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
           f"{urllib.parse.quote(article.replace(' ', '_'), safe='')}/daily/{start:%Y%m%d}/{end:%Y%m%d}")
    try:
        d = _fetch(url, ttl_min=6 * 60)
    except urllib.error.HTTPError:
        return []
    return [(i["timestamp"][:8], i["views"]) for i in d.get("items", [])]


# ---------------------------------------------------------------- images

def esa_image(page_url, expected_title):
    """An ESA/Webb or ESA/Hubble image (CC BY 4.0): downloads the large JPEG once, returns its path + credit.
    The page's own title must match what we wrote the post about, so a wrong id can never slip through."""
    import html as H
    page = _fetch(page_url, ttl_min=7 * 24 * 60, raw=True).decode("utf-8", "replace")
    title = H.unescape(re.sub(r"<[^>]+>", "", (re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S) or [None, ""])[1])).strip()
    if title.lower() != expected_title.lower():
        raise ValueError(f"{page_url}: page title {title!r} != {expected_title!r}")
    m = re.search(r"Credit:</[^>]+>\s*(.*?)</div>", page, re.S)
    credit = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", m.group(1)))).split("Acknowledgement")[0].strip() if m else ""
    if not credit.startswith(("ESA/Webb", "ESA/Hubble")):
        raise ValueError(f"{page_url}: unexpected credit {credit!r}")
    big = re.search(r"https://cdn\.esa(?:webb|hubble)\.org/archives/images/large/[\w-]+\.jpg", page)
    if not big:
        raise ValueError(f"{page_url}: no large JPEG")
    path = os.path.join(ROOT, "assets", "cache", os.path.basename(big.group(0)))
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(_fetch(big.group(0), ttl_min=0, raw=True, timeout=180))
    return {"path": path, "credit": credit, "title": title}


def nasa_image(nasa_id):
    """A NASA Image & Video Library photo: downloads the biggest file once, returns its path + credit.
    NASA media is public domain, but some photos are third-party; we only accept NASA-credited ones."""
    meta = _fetch(f"https://images-api.nasa.gov/search?nasa_id={urllib.parse.quote(nasa_id)}", ttl_min=7 * 24 * 60)
    item = meta["collection"]["items"][0]["data"][0]
    hrefs = [i["href"] for i in _fetch(f"https://images-api.nasa.gov/asset/{urllib.parse.quote(nasa_id)}",
                                        ttl_min=7 * 24 * 60)["collection"]["items"]]
    pick = next((h for size in ("~orig.", "~large.") for h in hrefs if size in h and h.lower().endswith((".jpg", ".jpeg", ".png"))), None)
    if not pick:
        raise ValueError(f"{nasa_id}: no usable image file")
    path = os.path.join(ROOT, "assets", "cache", nasa_id + os.path.splitext(pick)[1].lower())
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(_fetch(pick.replace("http://", "https://"), ttl_min=0, raw=True, timeout=180))
    desc = item.get("description", "")
    if re.search(r"(credit|courtesy)[^.\n]{0,40}(spacex|blue origin|boeing|getty|ap photo|reuters|roscosmos|esa\b)", desc, re.I):
        raise ValueError(f"{nasa_id}: third-party photo, not public domain")
    who = (item.get("photographer") or item.get("secondary_creator") or "").strip()
    if who.upper().startswith("NASA"):
        credit = who
    elif nasa_id.lower().startswith("iss") and not who:
        credit = "NASA"                       # space station crew photo
    elif nasa_id.lower().startswith("iss") and re.search(rf"NASA astronaut {re.escape(who)}", desc):
        credit = f"NASA/{who}"                # taken by a NASA astronaut aboard the station
    elif re.search(r"credit:?\s*\(?NASA", desc, re.I):
        credit = re.search(r"credit:?\s*\(?(NASA[^)\n]*)", desc, re.I).group(1).strip()
    else:
        raise ValueError(f"{nasa_id}: can't confirm a NASA credit (photographer {who!r})")
    return {"path": path, "credit": credit, "title": item.get("title", ""), "description": item.get("description", ""),
            "date": (item.get("date_created") or "")[:10], "nasa_id": nasa_id}
