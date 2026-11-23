# Liftoff Daily tuning log

## 2026-11-01: page designed and first formats built (Claude, with the owner)
- Name: Liftoff Daily, @liftoff_daily (open on IG + TikTok). Plan in PLAYBOOK.md.
- Built: data feeds (liftoff/sources.py), check gate (liftoff/checks.py), photo Reel engine with original ambient music
  (liftoff/video.py, liftoff/music.py), formats: Look Up countdown, Launch Week, Aurora alert (liftoff/reels.py).
- All jobs are preview-only (live=False). Samples are in samples/.
- Next to build: Scale comparisons, Just In news, git repo + Jarvis hookup.

## 2026-11-02: renamed to Liftoff Daily, Wow format, profile picture
- Owner picked **Liftoff Daily, @liftoff_daily** (open on IG, TikTok, YouTube). Folder is now LiftoffDaily/, package liftoff/.
  Lookalike to watch: @liftoffdaily (no underscore) is a small aviation creator.
- New format **Wow** (Tue 12:00, Sat 10:00 PT): a telescope image plus 3 facts, from a hand-checked queue (liftoff/wow.py).
  Images come from NASA's library or ESA/Webb and ESA/Hubble (CC BY 4.0); the release page's title and credit are checked
  live. Queue: Cosmic Cliffs (NASA Webb), N159 (ESA/Webb picture of the month, Oct 2026).
  Caught during review: N159's "230 light-years" is the width of the *image*, not the cloud. Fixed the wording.
- Profile picture: brand/profile_pic.png (gold rocket on a night sky; readable at 76px).
- Calendar now has ~3-4 Reels/week plus event days. Still need Scale and Just In formats to reach 2 a day.

## 2026-11-02 (evening): live
- Owner approved the previews and went live. All 7 jobs are live=True; posting also needs the repo variable POSTING_ENABLED=true.
- First posts: Tue Nov 3 11:00 Geminids "6 weeks away", Tue 12:00 Wow Cosmic Cliffs, Sat Wow N159,
  Mon Nov 9 Launch Week + Leonids "1 week". Aurora whenever NOAA issues a G2+ watch.
- Baseline to beat: the other pages' ~100-140 reach per Reel and 0 shares. Watch: reach, shares per reach, watch time vs length.
- About 3 posts a week for now; the Scale and Just In formats are next, to reach 2 a day.

## 2026-11-05 (Thu, check-in)

**Numbers (first 4 days):** 2 followers. 2 Reels. Look Up "Geminids 6 weeks away": 108 reach, 142 views, **2 shares**
(~1.9% shares per reach, the first shares on any of the three pages), 5.6 s avg watch on a 12.6 s Reel.
Wow "Cosmic Cliffs": 46 reach, 1.4 s avg watch on 11.2 s: most viewers left in the first second or two.
No errors in the run log; aurora jobs correctly skipped (no G2+ watch).

**Changed:** nothing. One post per format is far too little to judge.

**Watch Monday Nov 9 (review + queue upkeep):** the Wow queue has only 1 unposted entry (N159, Sat Nov 7), so Tue
Nov 10 has nothing unless Monday adds at least 4 (rule: keep 4+). sky.py only goes to the Geminids (Dec 13): stock it
through early January (Ursids, Quadrantids, Moon events, two sources each). Compare Sat's Wow (N159) first-second hold
against Cosmic Cliffs; if Wow stays under ~2 s watch, rework its first frame toward the Look Up style.

## 2026-11-09 (Mon, Jarvis full review + queue upkeep)

**Numbers (first week):** 4 followers. 4 Reels. Look Up "Geminids 6 weeks away": 114 reach, **2 shares**, 2 comments,
5.9 s watch. Wow N159: 138 reach, 3.0 s. Wow Cosmic Cliffs: 49 reach, 2.4 s. Launch Week (this morning): 5 reach so
far, 1 save. Aurora correctly skipped all week (no G2+ watch). No errors.

**Changed:**
1. **Wow queue refilled (was empty: Tue Nov 10 would have skipped).** Four new ESA/Webb entries, every fact taken from
   the release text: Treasure Chest (potm2607a: ~70 young stars, biggest ~19x the Sun, carved by stars like Eta
   Carinae), "Gravity is copying these galaxies" (potm2609a: lensing cluster, 300x+ magnified clumps, a galaxy seen
   4+ times, twice in one cluster), OMC-2 "every stage of star birth" (potm2605a: 2.5 light-years across, 1,280 ly),
   Arp 263 "Where did its partner go?" (potm2608a). Hooks are punchier/curiosity-first because Wow holds only 2.4-3.0 s
   vs Look Up's 5.9 s. All four built, image titles and credits checked live, covers checked.
2. **Bug fix (liftoff/video.py):** very wide panoramas (OMC-2) crashed the build ("box offset can't be negative"): after
   the rounded resize the crop window was a fraction of a pixel bigger than the photo. The crop is now clamped.
3. **Sky queue:** added the Quadrantids (night of Jan 3, 2027). IMO 2027 calendar: max Jan 4 03:25 UT, ZHR 80; AMS:
   peak night Jan 3-4, ~25/hour under dark skies. The Reel says "around 25 an hour" (the number both support for a
   real sky). Moon from USNO at build time: 15%, rising ~5am. **Ursids skipped on purpose**: ZHR ~10, a ~90% Moon,
   and IMO vs AMS don't point to the same US night.

**Not built:** "Scale" format. The queues were the urgent gap, and one week of data is too thin to pick the next format.

**Watch Mon Nov 16 (first baseline review):** Leonids 1-week Reel (today 11am) and tonight's Reel on Nov 16. Do the new
Wow hooks hold past 3 s? Shares per reach: Look Up 1.8% vs Wow 0%. Decide on Scale vs Just In (wider-science preview).

## 2026-11-14 (Sat, Claude with the owner): more Look Up, less Wow

**Numbers (14 days):** Look Up 145 avg reach, 4 shares, 4.8 s watch (the winner); Wow 78 reach, 3.3 s; launch week 43.
8 followers.

**Changed:** Wow once a week (Saturday; Tuesday dropped). Look Up now handles full moons (kind="moon"): the Dec 23
supermoon is queued (1 week out on Dec 16, and the night itself). Every claim is computed and checked at build time:
full at 8:28 PM ET Dec 23 (USNO), 221,667 miles away (JPL Horizons), the closest full moon of 2026 (Horizons distance at
all 13 of 2026's full moons), rises around sunset (USNO: 4:33 PM rise, 5:02 PM sunset, central US), still 99% lit on
Christmas Eve (USNO). Photo: NASA/Bill Ingalls, Dec 2017 supermoon over Washington. Test builds: 22 checks, 0 blocking.

## 2026-11-16 (Mon, Jarvis full review: first baseline)

**Numbers (30 days, 9 Reels):** 8 followers. Look Up 150 avg reach, 4.5 shares avg, 4.8 s watch (Geminids 6-weeks: 183 reach,
9 shares). Wow 83 reach, 0 shares, 3.3 s. Launch Week 78 reach, 2.5 s. Look Up is still the winner, but n=2.

**Bug fixed (autopost.py): two Wow Reels posted Sat Nov 14.** The 10:30 run posted House of Mirrors. A queued run
(10:33) had checked out the repo as it was when it was triggered, so it didn't see that post: it rebuilt the same Reel
(Instagram rejected it, luckily) and wrote "error" over the "posted" record. The 10:45 run saw "error", retried, and
posted the next Wow (OMC-2). Fix, in all three pages' runners: (1) every CI run pulls the latest state first;
(2) right before publishing, re-check posted.json and today's run record, and stop as "duplicate" if it's already out;
(3) the run log is merged, never overwritten, and a "posted" record can't be downgraded. No check loosened.

**Wow queue refilled (1 left → 4):** Red Spider Nebula (potm2510a), M77 "core outshines the galaxy" (potm2604a),
MACS J0553 "two galaxy clusters crashed" (potm2606a), after Arp 263. Every fact copied from the ESA/Webb release text
(e.g. legs "each extend about 3 light-years"; black hole "eight million times as massive as our Sun"; "seen as it
was 4.4 billion years in the past"; arc = "three images of a single background galaxy"). Skipped potm2603a: it's two
discs side by side and a vertical crop would show one. All 4 built, 0 blocking, covers checked.
**Today's Leonids "tonight" Look Up (11am):** test-built, 0 blocking (Moon 43% lit, sets ~11pm, from USNO).

**Not changed:** Scale / Just In not built this week (the duplicate bug and empty queue came first; 9 posts is too
thin). Sky queue runs to Jan 3 (Geminids arc, Dec 23 supermoon, Quadrantids).

**Watch Thu Nov 19:** Leonids tonight Reel shares; no duplicate posts. Next Monday: build Scale (one new format).

## 2026-11-20 — Launch-day posts replace the weekly roundup (owner request)
- Weekly launch roundup averaged ~100 views; Starship Flight 15 (Nov 13) went by without its own post.
- New: one Reel per big launch (Starship, Artemis, crewed, New Glenn, Falcon Heavy, NASA science), morning of or the
  afternoon before an overnight launch. Firm time required; RocketLaunch.live must list it within 2 h of LL2.
- No SpaceX footage/photos (copyrighted). Our own night-sky art; NASA's photo for Artemis only.
- Launch outcome ("it landed!") posts need a second source for the result: Jarvis hand-verifies those (radar).

## 2026-11-23 (Mon, Jarvis full review)

**Numbers:** 9 followers. Only **2 Reels in 7 days** (Look Up Leonids tonight 120 reach / 2.7 s; Wow Arp 263 73 reach,
1 share). 30 days: Look Up 154 avg reach, 4.3 shares; Wow 83 reach, 3.2 s; launch week 82. The page is starved: there's
no sky countdown due until the Geminids 2-week stage on Nov 29.

**New format: Scale (`reel_scale`, Tue 12:00 PT, from tomorrow).** It's the PLAYBOOK's "mind-blown scale" pillar and the
planned next format. Same photo pipeline, credit check and caption checks as Wow, with a SCALE chip and its own
hand-checked queue (liftoff/scale.py). Every number agrees between NASA Science's fact pages and NASA Goddard's
planetary fact sheets; the checked values are written next to each entry.
- Sun: 1.3 million Earths fill it (NASA; fact sheet volume ratio 1,304,000); ~865,000 miles wide (fact sheet radius
  695,700 km = 864,600 mi, 109 Earths); 330,000+ times Earth's mass (fact sheet 332,900). Photo: SDO, Sept 10 2025
  (PIA26681), zoomed to crop SDO's timestamp.
- Pluto smaller than our Moon: 1,477 mi (NASA; fact sheet 2,376 km) vs the Moon's ~2,160 mi (NASA radius 1,080 mi;
  fact sheet 3,475 km); "about half the width of the United States"; dwarf planet since 2006 (IAU). Photo: New
  Horizons enhanced color (PIA19952); the caption says the colors are enhanced.
Skipped Jupiter: NASA's page says "1,000 Earths could fit inside" while the fact sheet's volume ratio is 1,321, so the
two sources don't agree in meaning. Will come back with the 11x-wider fact and a high-res NASA photo.
Test builds: 19 checks each, 0 blocking; covers checked.

**Wow queue +1 (3 → 4 unposted):** Markarian 178 (ESA/Hubble potw2549a): Wolf-Rayet stars "just before they collapse
into black holes or neutron stars", 13 million light-years, blue compact dwarf. Every line is from the release text.
Credit ESA/Hubble & NASA, F. Annibali, S. Hong. Test build 19 checks, 0 blocking.

**Fixed (insights.py):** network timeouts are retried.

**Watch Thu Nov 26:** first Scale Reel (Tue): shares per reach vs Look Up (4.3) and Wow (0.2). Shenzhou 24 launch_day_pm
(Tue 4pm). Next Monday: Scale needs 2+ more entries (Jupiter 11x wider, Earth vs Moon, Olympus Mons) if it beats Wow.
