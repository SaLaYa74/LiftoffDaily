"""Wow: one stunning telescope image, three facts that make you look again.

Hand-written queue: every hook and fact below comes from the image's own release text (linked in `source`),
checked by hand. Claude adds new entries during review runs from the ESA/Webb and ESA/Hubble
picture-of-the-month feeds and NASA releases. The builder posts the next unposted entry.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Wow:
    key: str
    image: tuple                  # ("nasa", nasa_id) or ("esa", page_url, exact page title)
    hook: str                     # *accent* words allowed
    hook_sub: str
    facts: tuple                  # ((line, sub, chip), ...) 2-3 beats
    send: str
    caption_lines: tuple          # plain-English facts for the caption
    source: str                   # where every fact above came from
    tags: str
    layout: str = "high"
    focus: tuple = ((0.5, 0.5), (0.5, 0.5))
    zoom: tuple = (1.0, 1.25)
    credit_as: str = ""           # how to print the credit when the library's form is terse


QUEUE = [
    Wow("cosmic-cliffs", ("nasa", "carina_nebula"),
        "These aren't *mountains*", "Webb photographed this, 7,600 light-years away",
        (("It's the edge of a giant *star nursery*", "NGC 3324, in the Carina Nebula", "WHAT YOU'RE SEEING"),
         ("The \"steam\" is *hot gas*", "Blasted off the wall by young stars' radiation", "LOOK CLOSER"),
         ("This light left about *7,600 years* ago", "Before humans invented writing", "WAIT, WHAT?")),
        "Send this to someone who needs *perspective*",
        ("These \"Cosmic Cliffs\" are the edge of a gigantic cavity in the star-forming region NGC 3324, "
         "in the Carina Nebula, roughly 7,600 light-years away.",
         "The \"steam\" rising off them is hot, ionized gas and dust streaming away, pushed by ultraviolet "
         "light from massive young stars.",
         "Webb's infrared camera revealed hundreds of stars that were hidden behind the dust."),
        "NASA Webb release, \"Cosmic Cliffs\" in the Carina Nebula (July 12, 2022)",
        "#jameswebb #webbtelescope #space #nebula #astronomy",
        layout="high", focus=((0.5, 0.62), (0.46, 0.6)), zoom=(1.0, 1.3), credit_as="NASA, ESA, CSA, STScI"),
    Wow("n159-cauldron", ("esa", "https://esawebb.org/images/potm2610a/", "Stars brewing in a nebulous cauldron"),
        "This view is *230 light-years* across", "And it's full of stars being born",
        (("161,000 light-years away", "In the Large Magellanic Cloud, a galaxy orbiting ours", "WHERE"),
         ("The orange smoke is *carbon* molecules", "Polycyclic aromatic hydrocarbons, lit up by starlight", "LOOK CLOSER"),
         ("Dark red threads hide *newborn stars*", "Shielded from the blast of the giants around them", "WAIT, WHAT?")),
        "Send this to someone who'd *zoom in*",
        ("This is N159, a star-forming region 161,000 light-years away in the Large Magellanic Cloud, a small "
         "galaxy orbiting the Milky Way. This one view spans about 230 light-years.",
         "The orange glow comes from polycyclic aromatic hydrocarbons, carbon-based molecules; the pale blue "
         "is hydrogen gas ionized by massive young stars.",
         "The dark red filaments are cold molecular hydrogen, the densest part of the cloud, where new stars are forming."),
        "ESA/Webb Picture of the Month potm2610a (Oct 22, 2026)",
        "#jameswebb #webbtelescope #space #nebula #astronomy",
        layout="low", focus=((0.5, 0.5), (0.54, 0.46)), zoom=(1.0, 1.3)),
]
