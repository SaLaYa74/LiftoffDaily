# Liftoff Daily: one-time setup (about 30-40 minutes)

✅ Already done: the GitHub repo exists and has all the code (Nov 2).

| # | Step | Where | Time |
|---|---|---|---|
| 1 | Create the Instagram account | Phone | 5 min |
| 2 | Reserve the TikTok + YouTube names | Phone | 5 min |
| 3 | Get the Instagram token, save it on your Mac | Computer | 10 min |
| 4 | Add 2 secrets to GitHub | Computer | 5 min |
| 5 | Copy the 15-minute timer | Computer (cron-job.org) | 5 min |
| 6 | Tell Claude "done" | Here | 1 min |

Nothing posts during any of this. Every job is preview-only until you give the final OK.

---

## 1. Create the Instagram account (phone)

1. In Instagram, go to your profile and tap your **username at the top**.
2. Tap **Add Instagram account**, then **Create new account**.
3. Fill in the account:
   - Username: **`liftoff_daily`** (with the underscore).
   - Name: **Liftoff Daily**.
4. Make it a Creator account:
   - Go to Profile → ☰ menu → **Account type and tools** → **Switch to professional account**.
   - Pick a category like *Science & Technology* (or *Education*).
   - Choose **Creator**.
5. Tap **Edit profile** and paste this bio:
   ```
   Liftoff Daily 🚀
   Launches, sky events & discoveries in 15 seconds
   Real NASA/ESA images · verified facts
   Look up 👆
   ```
6. Add the profile picture:
   - On your Mac, the file is `LiftoffDaily/brand/profile_pic.png`.
   - AirDrop it to your phone: right-click it in Finder → Share → AirDrop.
   - Then go to Edit profile → **Edit picture**.

**It worked if:** you can switch between your pages and see @liftoff_daily with the rocket picture.

## 2. Reserve the names (phone, optional but smart)

- **TikTok:** sign up with the username **`liftoff_daily`**.
- **YouTube:** create a channel with the handle **`@liftoff_daily`**.

You don't post anything yet. This just stops someone else from taking the names.

## 3. Instagram token (computer)

These are the same steps you did for Paycheck Math and SharpCharts. Your old notes are in `SharpCharts/API/IG API.pages`.

1. Go to **developers.facebook.com** → **My Apps** and open the app you used before.
2. Go to **Instagram** → **API setup with Instagram login** → **Generate access tokens**.
3. Click **Add account** and log in as **liftoff_daily**. Allow everything it asks.
4. If Meta says the account has to be a *tester*:
   - In the app: **App roles** → **Roles** → **Add People** → **Instagram Tester** → `liftoff_daily`.
   - Then in the Instagram app: Settings → **Website permissions** → **Apps and websites** → **Tester invites** → **Accept**.
   - Then try step 3 again.
5. Click **Generate token** next to liftoff_daily and copy it. It's one long string that starts with **IGAA**.
6. Save it on your Mac. Run this in Terminal, paste the token, and press Enter:
   ```bash
   python3 "$HOME/Documents/Social Media Accounts/LiftoffDaily/save_token.py"
   ```
   The token stays invisible while you paste. That's normal.

**It worked if:** it prints `✅ Saved. Token works for @liftoff_daily.`

**Keep the token copied** for step 4. Never paste it into a chat, including here.

## 4. GitHub secrets (computer)

1. Go to **github.com/SaLaYa74/LiftoffDaily**.
2. Click **Settings** (the top tab on the repo page, not your profile settings).
3. Go to **Secrets and variables** → **Actions**.
4. Click the green **New repository secret** button and add these two:
   - **Name `IG_TOKEN`.** Secret: paste the IGAA token from step 3. Click **Add secret**.
   - **Name `GH_PAT`.** Secret: the same GitHub token you used as `GH_PAT` on Paycheck Math. GitHub never shows old secrets again, so get it from your note `SharpCharts/API/Token for GH_PAT.pages`. Click **Add secret**.
5. **Only if that GitHub token is a "fine-grained" token:** it only works on the repos you picked, so add the new one.
   - Click your avatar → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens**.
   - Open the token → **Repository access** → add **LiftoffDaily** → **Update**.
   - If it's a *classic* token, skip this.
6. **Don't** create the `POSTING_ENABLED` variable yet. That's the last step, after you've seen previews.

**It worked if:** the Secrets page lists `IG_TOKEN` and `GH_PAT`.

## 5. Copy the 15-minute timer (cron-job.org)

Your other pages run because cron-job.org pokes GitHub every 15 minutes. Liftoff Daily needs its own copy of that timer.

1. Log in at **cron-job.org** and open your **Paycheck Math** job.
2. Copy it. Use **Clone** or **Copy** if the menu has it. If not, click **Create cronjob** and copy every field by hand:
   - URL
   - Every 15 minutes
   - Request method
   - Headers
   - Request body
3. In the URL, change **`PaycheckMath`** to **`LiftoffDaily`**. Change nothing else.
4. Save, then click **Test run**.

**It worked if:** github.com/SaLaYa74/LiftoffDaily → **Actions** tab shows an **Auto-post** run within a minute.

- A **green check** means it worked.
- A **"Nothing due"** message also means it worked.
- A **red X with a 401/403/404 error** means the token in that timer doesn't cover the new repo. Do the "fine-grained" fix from step 4 for that token too. It needs **Actions: read and write**.

## 6. Tell Claude "done"

From here Claude:
- Checks that the first preview runs build correctly.
- Fixes anything that breaks.
- Shows you the previews.

When you like what you see, Claude turns the jobs on. Then you do one last click:
- Repo **Settings** → **Secrets and variables** → **Actions** → **Variables** tab → **New repository variable**.
- Name `POSTING_ENABLED`, value `true`.

Then Liftoff Daily joins the Monday/Thursday Jarvis review. From that point it runs itself.
