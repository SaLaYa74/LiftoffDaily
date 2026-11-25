"""Liftoff Daily posting calendar (US Pacific). Edit freely; no workflow change needed.
live=False means PREVIEW (built + checked, not published). Owner approved going live on 2026-11-02."""
from dataclasses import dataclass

WINDOW_HOURS = 12
MAX_POSTS_PER_DAY = 3
MON, TUE, WED, THU, FRI, SAT, SUN = range(7)
EVERY_DAY = (MON, TUE, WED, THU, FRI, SAT, SUN)


@dataclass(frozen=True)
class Job:
    name: str
    builder: str
    days: tuple
    time: str
    live: bool = False
    note: str = ""
    trial: bool = False


JOBS = [
    # Moments, not the calendar: each of these checks every day and idles unless something is due.
    # Sky-event countdowns (6 weeks / 2 weeks / 1 week / tomorrow / tonight). 11am PT = 2pm ET: early enough to plan the night.
    # Nov 24 roundtable (owner: "Apply all"): on a big shower's peak night, a find-your-state cloud map at 9am PT
    # (NWS + MET Norway must agree). It replaces that day's "tonight" countdown; idles every other day.
    Job("skymap",      "reel_sky_map",     EVERY_DAY, "09:00", live=True, note="Reel: peak-night cloud map, every state (Geminids, Quadrantids)"),
    Job("lookup",      "reel_lookup",      EVERY_DAY, "11:00", live=True, note="Reel: sky-event countdown (meteor showers, supermoons)"),
    # Aurora: NOAA issues storm watches at any hour, so three chances a day; one post per night at most.
    Job("aurora_am",   "reel_aurora",      EVERY_DAY, "08:00", live=True, note="Reel: northern lights alert (NOAA G2+ watch)"),
    Job("aurora_pm",   "reel_aurora",      EVERY_DAY, "13:00", live=True, note="Reel: northern lights alert (NOAA G2+ watch)"),
    Job("aurora_eve",  "reel_aurora",      EVERY_DAY, "16:30", live=True, note="Reel: northern lights alert (NOAA G2+ watch)"),
    # Weekly
    # Nov 14: Wow drops to once a week (78 reach, ~3 s watch vs Look Up's 145 reach and shares); Saturday kept.
    # Nov 23 (Jarvis): Liftoff posted only 2 Reels in the last 7 days (sky calendar gap until Nov 29), so the planned
    # "Scale" format starts Tuesday noon. Same photo pipeline and hand-checked queue rules as Wow.
    Job("scale_tue",   "reel_scale",       (TUE,), "12:00", live=True, note="Reel: size comparison on a NASA photo (hand-checked queue in liftoff/scale.py)"),
    Job("wow_sat",     "reel_wow",         (SAT,), "10:00", live=True, note="Reel: telescope image + 3 facts (hand-checked queue in liftoff/wow.py)"),
    # Nov 20 (owner): the weekly launch roundup (~100 views) is retired for posts on the day of big launches
    # (Starship, Artemis, crewed, New Glenn, Falcon Heavy, NASA science). Morning check for today; afternoon check
    # catches overnight and early-morning launches. Idles on days with nothing big.
    Job("launch_day_am", "reel_launch_day", EVERY_DAY, "07:00", live=True, note="Reel: big launch today (LL2 + RocketLaunch.live)"),
    Job("launch_day_pm", "reel_launch_day", EVERY_DAY, "16:00", live=True, note="Reel: big launch tonight / early tomorrow"),
]
