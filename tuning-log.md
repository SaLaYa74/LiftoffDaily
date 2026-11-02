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
