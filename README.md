# Liftoff Daily (@liftoff_daily)

Space in 15 seconds: launches, sky events, new images, discoveries. Strategy: **PLAYBOOK.md**.

- Calendar: `liftoff/schedule.py` (live=False = preview only) · runner: `autopost.py` (GitHub Actions, every 15 min)
- Formats: `liftoff/reels.py` (Look Up, Launch Week, Aurora, Wow) · hand-checked queues: `liftoff/sky.py`, `liftoff/wow.py` · data: `liftoff/sources.py` · checks: `liftoff/checks.py` (any BLOCK = no post)
- Kill switch: repo variable `POSTING_ENABLED` · secrets: `IG_TOKEN`, `GH_PAT`
- Preview locally: `python3 autopost.py --list`, `python3 autopost.py launch_week`
- Analytics (local only): `python3 insights.py` · save token: `python3 save_token.py`
- Profile picture: `brand/profile_pic.png` (source: `brand/profile.html`)
