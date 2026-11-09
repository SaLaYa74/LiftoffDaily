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
    # ---- added 2026-11-09 (Jarvis Monday review); every fact checked against the linked ESA/Webb release text ----
    Wow("treasure-chest", ("esa", "https://esawebb.org/images/potm2607a/", "Webb opens a Treasure Chest filled with stars"),
        "This *treasure chest* is full of stars", "Webb found it 7,500 light-years away",
        (("About *70 young stars* hide inside", "A compact cluster wrapped in gas and dust", "WHAT YOU'RE SEEING"),
         ("The biggest is *~19x* the Sun's mass", "A rare O-type star", "LOOK CLOSER"),
         ("Carved by giants like *Eta Carinae*", "One of its stars is ~5 million times brighter than the Sun", "WAIT, WHAT?")),
        "Send this to someone who loves *hidden treasure*",
        ("The \"Treasure Chest\" is a cometary globule in the Carina Nebula, about 7,500 light-years away: a cloud of gas "
         "and dust with a dense head and a sweeping tail.",
         "Inside is a compact cluster of about 70 young stars. The most massive is a rare O-type star roughly 19 times "
         "the mass of the Sun, and the cluster is likely around 1.3 million years old.",
         "Its shape was carved mostly by radiation and winds from massive stars nearby, including Eta Carinae, a system "
         "with a star about 5 million times as luminous as the Sun."),
        "ESA/Webb Picture of the Month potm2607a (Aug 6, 2026)",
        "#jameswebb #webbtelescope #space #nebula #astronomy"),
    Wow("house-of-mirrors", ("esa", "https://esawebb.org/images/potm2609a/", "Galaxies in a cosmic house of mirrors"),
        "Gravity is *copying* these galaxies", "A giant cluster bends light like a fun-house mirror",
        (("The golden blobs are *one galaxy cluster*", "Seen as it was when the Universe was ~8 billion years old", "WHAT YOU'RE SEEING"),
         ("Its gravity *bends light* from behind it", "Some tiny clumps look magnified 300+ times", "LOOK CLOSER"),
         ("Some galaxies show up *4+ times*", "Seen twice in this one cluster: a first", "WAIT, WHAT?")),
        "Send this to someone who loves *mind-benders*",
        ("The golden galaxies are the cluster MACS J0454.1-0300, seen as it was when the Universe was about 8 billion "
         "years old. The orange ones are much farther away, behind it.",
         "The cluster's huge mass bends and magnifies light from the galaxies behind it (gravitational lensing), "
         "stretching them into arcs. Some small clumps appear magnified more than 300 times.",
         "Rarely, lensing shows the same galaxy four or more times. Researchers spotted that twice in this cluster, the "
         "first time it has been seen more than once in the same galaxy cluster."),
        "ESA/Webb Picture of the Month potm2609a (Sep 29, 2026)",
        "#jameswebb #webbtelescope #space #galaxies #astronomy"),
    Wow("omc2-star-birth", ("esa", "https://esawebb.org/images/potm2605a/", "Webb unveils young stars across every stage of formation"),
        "Every stage of *star birth*, in one shot", "Webb looked behind the Orion Nebula",
        (("This scene is *2.5 light-years* across", "From star embryos to newborn stars, 1,280 light-years away", "WHAT YOU'RE SEEING"),
         ("The glowing ridges are *shockwaves*", "Jets from baby stars slamming into gas", "LOOK CLOSER"),
         ("Your eyes would see *nothing* here", "Dust blocks visible light; Webb sees infrared", "WAIT, WHAT?")),
        "Send this to someone who'd *zoom in*",
        ("This is part of OMC-2, a cloud of cold gas and dust behind the Orion Nebula, 1,280 light-years from Earth. "
         "The scene is about 2.5 light-years across and holds every stage of star formation.",
         "Jets from young protostars drive high-speed shockwaves into the gas around them; where they hit, the gas "
         "heats up and glows, making the sharp red ridges.",
         "Thick gas and dust block all visible light from OMC-2. Only in infrared, which Webb sees, do the protostars shine through."),
        "ESA/Webb Picture of the Month potm2605a (Jun 5, 2026)",
        "#jameswebb #webbtelescope #space #orion #astronomy"),
    Wow("arp263-missing-partner", ("esa", "https://esawebb.org/images/potm2608a/", "Striking star clusters and irregular clumps"),
        "Where did its *partner* go?", "This galaxy is what's left after a merger",
        (("Its companion is *nowhere* to be found", "It may have dissolved into this galaxy", "THE MYSTERY"),
         ("The blue glow marks *new stars*", "Hydrogen gas lit up by young starlight", "LOOK CLOSER"),
         ("That huge bright star is *in our galaxy*", "Right in front; Arp 263 is 25 million light-years away", "WAIT, WHAT?")),
        "Send this to someone who loves a *mystery*",
        ("Arp 263 (NGC 3239) is an irregular galaxy in Leo, about 25 million light-years away, believed to be the "
         "result of a past galactic merger.",
         "Its former companion is nowhere to be found: it may have been a dwarf galaxy that fully dissolved into "
         "Arp 263, or one too faint to spot.",
         "Blue shows hydrogen gas lit by young stars where new stars form. The big bright star, BD+17 2217, is in our "
         "own galaxy, right in front."),
        "ESA/Webb Picture of the Month potm2608a (Aug 27, 2026)",
        "#jameswebb #webbtelescope #space #galaxies #astronomy"),
]
