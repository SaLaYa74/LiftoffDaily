"""Scale: one NASA photo, one size comparison that makes you rethink how big things are. (Added 2026-11-23, Jarvis.)

Same hand-checked rules as Wow (liftoff/wow.py, same Wow record): every NUMBER must agree between two NASA sources
(the NASA Science fact page and NASA Goddard's planetary fact sheet, nssdc.gsfc.nasa.gov), and qualitative lines
are NASA's own wording. The checked values are written next to each entry. The builder posts the next unposted one.
"""
from .wow import Wow

QUEUE = [
    # NASA Science "Sun Facts": "it would take 1.3 million Earths to fill the Sun's volume"; "more than 330,000 Earths
    # to match the mass"; diameter "about 865,000 miles"; "Our Sun is a medium-sized star"; "Many stars are much larger".
    # NSSDC Sun fact sheet: volume ratio 1,304,000; mass ratio 332,900; mean radius 695,700 km (= 864,600 mi wide),
    # radius ratio 109.2.
    Wow("sun-million-earths", ("nasa", "PIA26681"),
        "*1.3 million* Earths would fit inside the Sun", "NASA's Solar Dynamics Observatory took this",
        (("More than *100 Earths* fit across it", "It's about 865,000 miles wide", "SIZE"),
         ("It outweighs Earth *330,000+ times*", "That's its mass, not just its size", "WEIGHT"),
         ("And it's only a *medium-sized* star", "Many stars are much larger", "WAIT, WHAT?")),
        "Send this to someone who thinks Earth is *big*",
        ("It would take about 1.3 million Earths to fill the Sun's volume.",
         "The Sun is about 865,000 miles wide: more than 100 Earths side by side. It's also more than 330,000 times "
         "as massive as Earth.",
         "Still, NASA calls it a medium-sized star. Many stars are much larger.",
         "This is a real image of the Sun from NASA's Solar Dynamics Observatory, taken Sept. 10, 2025."),
        "NASA Science, Sun Facts; NASA Goddard Sun Fact Sheet (volume 1,304,000 Earths, width 109 Earths, "
        "mass 332,900 Earths)",
        "#space #sun #nasa #astronomy #science",
        layout="low", focus=((0.5, 0.46), (0.5, 0.44)), zoom=(1.15, 1.3), credit_as="NASA/GSFC/SDO"),  # zoom crops SDO's timestamp
    # NASA Science "Pluto Facts": "equatorial diameter of about 1,477 miles (2,377 kilometers)"; "about half the width
    # of the United States"; "reclassified as a dwarf planet in 2006 by the International Astronomical Union".
    # NASA Science "Moon Facts": radius "about 1,080 miles (1,740 kilometers)" (= ~2,160 mi wide).
    # NSSDC: Pluto mean radius 1,188 km (2,376 km wide), Moon 1,737.4 km (3,475 km = 2,159 mi wide).
    Wow("pluto-smaller-than-moon", ("nasa", "PIA19952"),
        "Pluto is *smaller* than our Moon", "NASA's New Horizons took this in 2015",
        (("Pluto: about *1,477 miles* wide", "Our Moon: about 2,160 miles", "SIZE"),
         ("About *half the width* of the U.S.", "NASA's own comparison", "PICTURE IT"),
         ("It was a planet until *2006*", "Now it's officially a dwarf planet", "WAIT, WHAT?")),
        "Send this to someone who still *counts Pluto*",
        ("Pluto is about 1,477 miles (2,377 km) wide. Our Moon is about 2,160 miles (3,475 km) wide, so Pluto is the "
         "smaller of the two.",
         "NASA puts it this way: Pluto is only about half the width of the United States.",
         "It was reclassified as a dwarf planet in 2006 by the International Astronomical Union.",
         "This is a real enhanced-color view of Pluto from NASA's New Horizons flyby on July 14, 2015 (colors "
         "boosted to show differences on the surface)."),
        "NASA Science, Pluto Facts and Moon Facts; NASA Goddard Pluto and Moon Fact Sheets",
        "#space #pluto #nasa #astronomy #science",
        layout="low", focus=((0.5, 0.5), (0.5, 0.45)), zoom=(1.0, 1.2), credit_as="NASA/JHUAPL/SwRI"),
]
