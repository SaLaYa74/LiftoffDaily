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
