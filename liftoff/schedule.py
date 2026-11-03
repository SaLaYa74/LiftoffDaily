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
    Job("lookup",      "reel_lookup",      EVERY_DAY, "11:00", live=True, note="Reel: sky-event countdown (meteor showers, supermoons)"),
    # Aurora: NOAA issues storm watches at any hour, so three chances a day; one post per night at most.
    Job("aurora_am",   "reel_aurora",      EVERY_DAY, "08:00", live=True, note="Reel: northern lights alert (NOAA G2+ watch)"),
    Job("aurora_pm",   "reel_aurora",      EVERY_DAY, "13:00", live=True, note="Reel: northern lights alert (NOAA G2+ watch)"),
    Job("aurora_eve",  "reel_aurora",      EVERY_DAY, "16:30", live=True, note="Reel: northern lights alert (NOAA G2+ watch)"),
    # Weekly
    Job("wow_tue",     "reel_wow",         (TUE,), "12:00", live=True, note="Reel: telescope image + 3 facts (hand-checked queue in liftoff/wow.py)"),
    Job("wow_sat",     "reel_wow",         (SAT,), "10:00", live=True, note="Reel: telescope image + 3 facts (hand-checked queue in liftoff/wow.py)"),
    Job("launch_week", "reel_launch_week", (MON,), "07:00", live=True, note="Reel: rockets launching this week (LL2 + RocketLaunch.live)"),
]
