"""Sky events people can see with their own eyes, each one checked by hand against two sources.

Dates are the US evening a person would go outside ("peak night Dec 13" = the night of Dec 13-14).
Moon claims are NOT typed in here: reels.py works them out from the US Naval Observatory phases at build time
and blocks the post if the wording doesn't match the Moon that night.
"""
from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class SkyEvent:
    key: str
    name: str
    kind: str                     # "meteors" | "moon"
    night: date                   # the evening to go outside (US)
    headline: str                 # what it is, in a few words
    rate: int = 0                 # meteors: zenithal hourly rate (perfect dark sky, radiant overhead)
    best: str = ""                # when to look, local time
    where: str = ""               # where to look
    fact: str = ""                # the "wait, what?" kicker
    photo: str = ""               # NASA Image Library id
    photo_note: str = ""          # what the photo actually shows (goes in the caption)
    photo_focus: tuple = ((0.5, 0.5), (0.5, 0.5))    # push-in path, 0-1 photo coords (start, end)
    photo_zoom: tuple = (1.0, 1.2)
    sources: tuple = field(default_factory=tuple)


EVENTS = [
    SkyEvent("leonids-2026", "Leonids", "meteors", date(2026, 11, 16),
             "the Leonid meteor shower", rate=15,
             best="after midnight until dawn", where="anywhere overhead; they streak out of Leo, rising in the east",
             fact="They're comet dust hitting our air at nearly 160,000 mph",
             photo="NHQ202108100009", photo_note="a 2021 Perseid meteor and the Milky Way over West Virginia",
             photo_focus=((0.5, 0.5), (0.48, 0.42)), photo_zoom=(1.0, 1.12),
             sources=("IMO 2026 Meteor Shower Calendar: maximum Nov 17", "American Meteor Society: peak night Nov 16-17")),
    SkyEvent("geminids-2026", "Geminids", "meteors", date(2026, 12, 13),
             "the Geminid meteor shower, the strongest of the year", rate=150,
             best="from 10pm, best around 2am", where="anywhere overhead; they fan out from Gemini, high in the east",
             fact="They come from an asteroid, 3200 Phaethon, not a comet",
             photo="NHQ202108100009", photo_note="a 2021 Perseid meteor and the Milky Way over West Virginia",
             photo_focus=((0.5, 0.5), (0.48, 0.42)), photo_zoom=(1.0, 1.12),
             sources=("IMO 2026 Meteor Shower Calendar: ZHR 150", "American Meteor Society: peak night Dec 13-14, ZHR 150")),
]


def upcoming(today, horizon_days=60):
    return [e for e in EVENTS if 0 <= (e.night - today).days <= horizon_days]
