"""Liftoff Daily Reels. Every claim comes from liftoff.sources / liftoff.sky and passes its checks first."""
import math
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from . import checks as C
from . import look as K
from . import sky as SKY
from . import sources as S
from .core import DataError, NoContent, Post
from .video import Beat, photo_reel, video_checks

PT = ZoneInfo("America/Los_Angeles")
SYNODIC = 29.530589

# Countdown arc for sky events: (days before the night, label). Big events get every stage, small ones two.
ARC_BIG = [(42, "6 weeks"), (14, "2 weeks"), (7, "1 week"), (1, "tomorrow"), (0, "tonight")]
ARC_SMALL = [(7, "1 week"), (0, "tonight")]
STAGE_GRACE = {42: 7, 14: 1, 7: 1, 1: 0, 0: 0}     # how many days late a stage may still post (retries)


def _post(key, mp4, cover, caption, rep):
    video_checks(rep, mp4)
    C.image(rep, cover, "reel")
    C.caption(rep, caption)
    return Post(key=key, caption=caption, images=[{"reel": mp4, "cover": cover}], media="reel", checks=rep)


def _night_range(d):
    nxt = d + timedelta(days=1)
    return f"{d:%b} {d.day}-{nxt.day}" if nxt.month == d.month else f"{d:%b} {d.day}-{nxt:%b} {nxt.day}"


# ---------------------------------------------------------------- the Moon on a given night

def _clock(t):
    """21:14 → '9pm', 23:50 → 'midnight', 00:40 → '1am' (nearest hour; good enough for 'around')."""
    h = (t.hour + (t.minute >= 30)) % 24
    return "midnight" if h == 0 else ("noon" if h == 12 else f"{h % 12}{'am' if h < 12 else 'pm'}")


def moon_on(night, rep):
    """The Moon on a viewing night, from two US Naval Observatory products that must agree:
    the phase calendar (we compute age and lit fraction) and the one-day almanac for the middle of the US
    (lit fraction, moonrise/moonset). Returns (lit_pct, claim, sub, caption_note)."""
    when = datetime.combine(night + timedelta(days=1), time(3, 0), tzinfo=timezone.utc)    # ~9pm central
    phases = S.moon_phases(night - timedelta(days=32), 10)
    news = [t for t, p in phases if p == "New Moon" and t <= when]
    if not rep.require(bool(news), "moon: USNO new moon found", f"no new moon before {when:%Y-%m-%d}"):
        raise DataError("USNO phases missing")
    age = (when - news[-1]).total_seconds() / 86400
    lit_calc = 100 * (1 - math.cos(2 * math.pi * age / SYNODIC)) / 2
    today, tomorrow = S.moon_day(night), S.moon_day(night + timedelta(days=1))
    C.agree(rep, "moon: lit %", lit_calc, today["lit"], 12, "%")
    waxing = age < SYNODIC / 2
    rep.require(("Waxing" in today["phase"] or "First" in today["phase"] or "New" in today["phase"]) == waxing
                or "Full" in today["phase"], "moon: waxing/waning agrees with USNO", f"{today['phase']} at age {age:.1f}d")
    evening_set = today["set"] if today["set"] and today["set"].hour >= 12 else (
        tomorrow["set"] if tomorrow["set"] and tomorrow["set"].hour < 12 else None)
    evening_rise = today["rise"] if today["rise"] and today["rise"].hour >= 12 else (
        tomorrow["rise"] if tomorrow["rise"] and tomorrow["rise"].hour < 12 else None)
    lit = today["lit"]
    if age < 1.5 or age > 28:
        claim, sub, note = "No Moon at all", "The darkest skies you can get", "new Moon"
    elif waxing and age < 13 and evening_set:
        thin = "A thin crescent Moon" if lit < 35 else "The Moon"
        claim, sub = f"{thin} sets around {_clock(evening_set)}", "Then it's dark skies"
        note = f"sets around {_clock(evening_set)} in the central US"
    elif 13 <= age <= 16.5:
        claim, sub, note = "A bright full Moon is up all night", "You'll still catch the bright ones", "full Moon"
    elif not waxing and evening_rise:
        claim, sub = f"The Moon rises around {_clock(evening_rise)}", "Look before then"
        note = f"rises around {_clock(evening_rise)} in the central US"
    else:
        raise DataError(f"no clear moon story for {night} (age {age:.1f}d, {today})")
    rep.require(0 <= lit <= 100, "moon: lit fraction in range", f"{lit}")
    return lit, claim, sub, note


# ---------------------------------------------------------------- Look Up: sky event countdown

def _due_stage(event, today, posted):
    arc = ARC_BIG if event.rate >= 100 else ARC_SMALL
    left = (event.night - today).days
    for days, label in arc:
        if days - STAGE_GRACE[days] <= left <= days and f"lookup-{event.key}-{days}" not in posted:
            return days, label
    return None


def _hook(event, days, label, left):
    if days == 0:
        return (f"*Tonight*: up to {event.rate} shooting stars an hour" if event.rate >= 50
                else f"*Tonight*: the {event.name} peak"), "The night to look up"
    if days == 1:
        return "*Tomorrow night*, look up", f"The {event.name} peak"
    when = f"{round(left / 7)} weeks" if left >= 14 else ("1 week" if left == 7 else f"{left} days")
    if days == 42 and event.rate >= 100:
        return f"The best meteor shower of {event.night.year} is *{when}* away", ""
    return f"*{when.capitalize()}* until the {event.name}", f"Night of {_night_range(event.night)}"


def reel_lookup(out_dir, posted=None, today=None):
    posted = posted or {}
    today = today or datetime.now(PT).date()
    due = [(e, _due_stage(e, today, posted)) for e in SKY.upcoming(today)]
    due = sorted([(e, s) for e, s in due if s], key=lambda es: es[1][0])        # most urgent first
    if not due:
        raise NoContent("no sky-event countdown due today")
    ev, (days, label) = due[0]
    rep = C.Report(f"lookup {ev.key} {label}")
    rep.require(len(ev.sources) >= 2, "event: two independent sources", f"{ev.key} lists {len(ev.sources)}")
    rep.require(days - STAGE_GRACE[days] <= (ev.night - today).days <= days,
                "event: countdown wording matches the date", f"{label} vs {(ev.night - today).days} days")
    lit, moon, moon_sub, moon_note = moon_on(ev.night, rep)
    photo = S.nasa_image(ev.photo)
    C.credit(rep, photo["credit"])

    big, small = _hook(ev, days, label, (ev.night - today).days)
    lay = "low"
    beats = [Beat(K.hook(big, small, chip="LOOK UP", layout=lay), 2.3)]
    if ev.rate >= 50:
        beats.append(Beat(K.stat(str(ev.rate), "shooting stars *an hour*", "In a perfectly dark sky", layout=lay), 2.0))
    beats += [
        Beat(K.line(_night_range(ev.night), sub=f"Best {ev.best}", chip="WHEN", layout=lay), 2.1),
        Beat(K.line(moon, sub=moon_sub, chip="THE MOON", layout=lay), 2.0),
        Beat(K.line(ev.fact, chip="WAIT, WHAT?", layout=lay), 2.3),
        Beat(K.send("Send this to who you're *watching with*", "Follow for the night-of reminder 🔭", layout=lay), 1.9),
    ]
    key = f"lookup-{ev.key}-{days}"
    mp4, cover = photo_reel(out_dir, key, photo["path"], f"Photo: {photo['credit']}", beats, seed=key,
                            focus=ev.photo_focus, zoom=ev.photo_zoom, layout=lay, grade=(1.12, 1.18, 1.3))
    plain = big.replace("*", "")
    rate_line = (f"Up to {ev.rate} meteors an hour in a perfectly dark sky (real-world counts are lower, "
                 f"but still a show)." if ev.rate >= 50 else f"Expect around {ev.rate} an hour from a dark spot.")
    caption = "\n".join([
        f"{plain} 🌠",
        "",
        f"{ev.name}: peak night {_night_range(ev.night)}. {rate_line}",
        f"Best time: {ev.best}. Where to look: {ev.where}.",
        f"Moon: {lit}% lit, {moon_note}.",
        f"Wait, what? {ev.fact}.",
        "",
        "📤 Send this to who you're watching with. 🔔 Follow for the night-of reminder.",
        "",
        f"Source: {'; '.join(ev.sources)}. Moon: US Naval Observatory.",
        f"Photo: {ev.photo_note} ({photo['credit']}).",
        f"#{ev.name.lower()} #meteorshower #stargazing #space #astronomy",
    ])
    return _post(key, mp4, cover, caption, rep)


BUILDERS = {"reel_lookup": reel_lookup}


# ---------------------------------------------------------------- Launch: this week's launches (Mondays)

ET = ZoneInfo("America/New_York")
EXACT = ("Second", "Minute", "Hour", "Morning", "Afternoon", "Day")        # LL2 precisions we'll print a date for
NOTABLE = (("Starship", 100), ("Artemis", 100), ("Crew", 90), ("Axiom", 90), ("Shenzhou", 85), ("Soyuz MS", 85),
           ("New Glenn", 75), ("Falcon Heavy", 75), ("Neutron", 70), ("Vulcan", 65), ("Ariane 6", 65), ("H3", 60))
SCIENCE = ("Planetary Science", "Astrophysics", "Heliophysics", "Earth Science", "Human Exploration", "Resupply")
LAUNCH_PHOTO = "SLS_MAF_20260401_ArtemisIILaunch_09"
LAUNCH_PHOTO_NOTE = "the Artemis II launch, April 1, 2026"


def _rocket(l):
    return l["rocket"].replace(" Block 5", "").strip()


def _mission(l):
    m = l["mission"].replace("TBD", "").replace("?", "").strip(" -")
    return m if m and "unknown" not in m.lower() else ""


def launch_score(l):
    """How much a general audience cares: crewed and giant rockets first, Starlink and secret payloads last."""
    text = f"{l['rocket']} {l['name']} {l['mission']}".lower()
    s = max([v for k, v in NOTABLE if k.lower() in text] or [0])
    if l["mission_type"] in SCIENCE:
        s = max(s, 60)
    if not s:
        s = 5 if "starlink" in text else (35 if "falcon 9" in text else 20)
    return s if _mission(l) else min(s, 4)


def reel_launch_week(out_dir, posted=None, now=None):
    posted = posted or {}
    now = now or datetime.now(timezone.utc)
    week = now.astimezone(ET).isocalendar()
    key = f"launchweek-{week[0]}-w{week[1]:02d}"
    if key in posted:
        raise NoContent(f"{key} already posted")
    rep = C.Report(key)
    end = now + timedelta(days=7)
    every = S.launches(limit=40)
    soon = [l for l in every if l["net"] and now <= l["net"] < end and l["status"] not in ("Success", "Failure")]
    dated = [l for l in soon if l["precision"] in EXACT]
    if len(dated) < 3:
        raise NoContent(f"only {len(dated)} launches with a firm date this week")
    rep.require(len({l["id"] for l in dated}) == len(dated), "launches: no duplicates", "duplicate launch ids")
    # Second source: RocketLaunch.live's next-5 list. Inside its horizon a launch must appear there too, or we leave
    # it out; beyond it we keep only launches LL2 marks Go / To Be Confirmed. The count only includes what survives.
    rll = S.launches_rll()
    horizon = max((r["t0"] for r in rll if r["t0"]), default=now)
    confirmed = [l for l in dated if (S.rll_match(l, rll) if l["net"] <= horizon else l["status"] in ("Go", "TBC"))]
    for l in dated:
        if l not in confirmed:
            rep.expect(False, f"launch: {_rocket(l)} {l['net'].astimezone(ET):%a %H:%M} ET left out",
                       "not confirmed by the second source" if l["net"] <= horizon else f"LL2 status {l['status']}")
    rep.require(any(l["net"] <= horizon for l in confirmed), "launches: second source overlaps this week",
                "RocketLaunch.live confirmed none of this week's launches")
    if len(confirmed) < 3:
        raise NoContent(f"only {len(confirmed)} confirmed launches this week")
    dated = confirmed
    top = sorted(dated, key=lambda l: (-launch_score(l), l["net"]))[:4]
    top.sort(key=lambda l: l["net"])
    photo = S.nasa_image(LAUNCH_PHOTO)
    C.credit(rep, photo["credit"])

    lay = "low"
    big = top[-1] if launch_score(top[-1]) >= max(launch_score(l) for l in top) else max(top, key=launch_score)
    rows = [(f"{l['net'].astimezone(ET):%a}".upper(), f"{_rocket(l)} · {_mission(l)}" if _mission(l) else _rocket(l))
            for l in top]
    beats = [
        Beat(K.hook(f"*{len(dated)}* rockets launch this week", "Here are the ones worth watching", chip="LAUNCH WEEK",
                    layout=lay), 2.3),
        Beat(K.rows("Worth *watching*", rows, layout=lay), 3.6),
        Beat(K.line(f"Biggest one: *{_rocket(big)}*", sub=f"{big['net'].astimezone(ET):%A %b} {big['net'].astimezone(ET).day} · "
                    f"{big['location'].split(',')[0]}", chip="DON'T MISS", layout=lay), 2.3),
        Beat(K.send("Send this to your *launch buddy*", "Follow for launch-day alerts 🚀", layout=lay), 1.9),
    ]
    mp4, cover = photo_reel(out_dir, key, photo["path"], f"Photo: {photo['credit']}", beats, seed=key,
                            focus=((0.55, 0.3), (0.58, 0.22)), zoom=(1.05, 1.2), layout=lay, grade=(0.92, 1.08, 1.1))
    listed = sorted(dated, key=lambda l: l["net"])
    lines = [f"{l['net'].astimezone(ET):%a %b} {l['net'].astimezone(ET).day} "
             f"{l['net'].astimezone(ET):%-I:%M %p} ET · {_rocket(l)}{' · ' + _mission(l) if _mission(l) else ''} "
             f"({l['provider']})" for l in listed[:10]]
    caption = "\n".join([
        f"{len(dated)} rockets are scheduled to launch this week 🚀",
        "",
        *lines,
        *([f"+ {len(listed) - 10} more"] if len(listed) > 10 else []),
        "",
        "Launch dates slip all the time; we post the moment the big ones go.",
        "📤 Send this to your launch buddy. 🔔 Follow for launch-day alerts.",
        "",
        "Source: The Space Devs Launch Library 2, cross-checked with RocketLaunch.live.",
        f"Photo: {LAUNCH_PHOTO_NOTE} ({photo['credit']}).",
        "#rocketlaunch #spacex #space #nasa #rocket",
    ])
    rep.require(all(l["net"] >= now for l in listed), "launches: all in the future", "a past launch slipped in")
    return _post(key, mp4, cover, caption, rep)


# ---------------------------------------------------------------- Aurora alert (NOAA storm watch, G2 or stronger)

AURORA_PHOTO = "iss047e000320"
AURORA_PHOTO_NOTE = "an aurora seen from the International Space Station, 2016"
G_TO_KP = {1: 5, 2: 6, 3: 7, 4: 8, 5: 9}


def reel_aurora(out_dir, posted=None, now=None, min_g=2):
    posted = posted or {}
    now = now or datetime.now(timezone.utc)
    tonight = (now.astimezone(PT) - timedelta(hours=6)).date()        # after midnight it is still last night
    utc_days = {(f"{d:%b}", d.day) for d in (tonight, tonight + timedelta(days=1))}   # US night spans 2 UTC dates
    watches = [w for w in S.swpc_messages("WATA") if now - w["issued"] < timedelta(hours=48)]
    best = None
    for w in watches:
        info = S.storm_watch(w["message"])
        g = max([lvl for day, lvl in info["levels"].items() if day in utc_days] or [0])
        if g >= min_g and (best is None or g > best[0]):
            best = (g, info, w)
    if not best:
        raise NoContent(f"no G{min_g}+ storm watch for tonight ({tonight})")
    g, info, w = best
    key = f"aurora-{tonight:%Y-%m-%d}-g{g}"
    if any(k.startswith(f"aurora-{tonight:%Y-%m-%d}") for k in posted):
        raise NoContent(f"aurora alert for {tonight} already posted")
    rep = C.Report(key)
    # Second NOAA product: the Kp forecast must reach the matching level within the next 30 hours
    kp = max([k for t, k, _ in S.kp_forecast() if now - timedelta(hours=3) <= t <= now + timedelta(hours=30)] or [0])
    rep.require(kp >= G_TO_KP[g] - 0.34, "aurora: Kp forecast backs the watch", f"watch G{g} but Kp max {kp}")
    rep.require(bool(info["aurora"]), "aurora: NOAA visibility line present", "no 'Aurora -' line in the watch")
    photo = S.nasa_image(AURORA_PHOTO)
    C.credit(rep, photo["credit"])

    noaa = info["aurora"].rstrip(".")
    lay = "low"
    beats = [
        Beat(K.hook("Northern lights alert: *tonight*", f"NOAA has a G{g} storm watch out", chip="LOOK UP", layout=lay), 2.3),
        Beat(K.line("How far south?", sub=f"NOAA: {noaa}", chip="WHERE", layout=lay), 2.8),
        Beat(K.line("Look *north*, away from city lights", sub="Best roughly 10pm to 2am", chip="HOW", layout=lay), 2.2),
        Beat(K.line("Your phone sees more than *your eyes*", sub="Use night mode, hold still 3 seconds", chip="PRO TIP",
                    layout=lay), 2.2),
        Beat(K.send("Send this to someone who's *never seen them*", "Follow for the next alert 🌌", layout=lay), 1.9),
    ]
    mp4, cover = photo_reel(out_dir, key, photo["path"], f"Photo: {photo['credit']}", beats, seed=key,
                            focus=((0.5, 0.5), (0.45, 0.45)), zoom=(1.0, 1.15), layout=lay, grade=(1.1, 1.1, 1.2))
    caption = "\n".join([
        "Northern lights alert for tonight 🌌",
        "",
        f"NOAA's Space Weather Prediction Center has a G{g} geomagnetic storm watch out (issued {w['issued']:%b} "
        f"{w['issued'].day}, {w['issued']:%H:%M} UTC). In NOAA's words: {noaa}.",
        "Look north from somewhere dark, roughly 10pm-2am. Phone night mode picks up color your eyes can't.",
        "Forecasts can change fast; clouds and city lights are the real enemies.",
        "",
        "📤 Send this to someone who's never seen them. 🔔 Follow for the next alert.",
        "",
        "Source: NOAA Space Weather Prediction Center (storm watch + Kp forecast).",
        f"Photo: {AURORA_PHOTO_NOTE} ({photo['credit']}).",
        "#northernlights #aurora #auroraborealis #space #nightsky",
    ])
    return _post(key, mp4, cover, caption, rep)


BUILDERS.update({"reel_launch_week": reel_launch_week, "reel_aurora": reel_aurora})


# ---------------------------------------------------------------- Wow: telescope image of the day (hand-checked queue)

def reel_wow(out_dir, posted=None):
    from .wow import QUEUE
    posted = posted or {}
    todo = [w for w in QUEUE if f"wow-{w.key}" not in posted]
    if not todo:
        raise NoContent("wow queue is empty: add entries to liftoff/wow.py")
    w = todo[0]
    key = f"wow-{w.key}"
    rep = C.Report(key)
    rep.require(2 <= len(w.facts) <= 3, "wow: 2-3 fact beats", f"{len(w.facts)} beats")
    rep.require(bool(w.source), "wow: facts cite the release", "no source")
    img = S.nasa_image(w.image[1]) if w.image[0] == "nasa" else S.esa_image(w.image[1], w.image[2])
    C.credit(rep, img["credit"])
    credit = w.credit_as or img["credit"]
    beats = [Beat(K.hook(w.hook, w.hook_sub, chip="WOW", layout=w.layout), 2.4)]
    beats += [Beat(K.line(a, sub=b, chip=c, layout=w.layout), 2.3) for a, b, c in w.facts]
    beats.append(Beat(K.send(w.send, "Follow for a new one every week 🔭", layout=w.layout), 1.9))
    mp4, cover = photo_reel(out_dir, key, img["path"], f"Image: {credit}", beats, seed=key,
                            focus=w.focus, zoom=w.zoom, layout=w.layout)
    caption = "\n".join([
        f"{w.hook.replace('*', '')} 🤯",
        "",
        *w.caption_lines,
        "",
        "📤 Send this to someone who'd love it. 📌 Save it as a wallpaper.",
        "",
        f"Source: {w.source}.",
        f"Image: {credit}.",
        w.tags,
    ])
    return _post(key, mp4, cover, caption, rep)


BUILDERS["reel_wow"] = reel_wow
