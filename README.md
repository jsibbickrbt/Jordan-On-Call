# Jordan On-Call Calendar

Auto-generated ICS calendar feed containing only Jordan's on-call shifts, filtered from the RBT Work Calendar.

Updated automatically every day at 6 AM UTC via GitHub Actions.

---

## Setup Instructions

### Step 1 — Create the repo

1. Go to [github.com](https://github.com) and sign in
2. Click **New repository**
3. Name it something like `jordan-oncall-calendar`
4. Set it to **Public** (required for GitHub Pages free hosting)
5. Click **Create repository**

### Step 2 — Upload the files

Upload these files maintaining the folder structure:

```
generate.py
docs/
  jordan_oncall.ics
.github/
  workflows/
    update_calendar.yml
README.md
```

The easiest way: click **Add file → Upload files** in your new repo, then drag all files in.

### Step 3 — Enable GitHub Pages

1. Go to your repo **Settings**
2. Click **Pages** in the left sidebar
3. Under **Source**, select **Deploy from a branch**
4. Set branch to `main`, folder to `/docs`
5. Click **Save**

After a minute or two, GitHub Pages will be live.

### Step 4 — Run the Action manually (first time)

1. Go to the **Actions** tab in your repo
2. Click **Update Jordan On-Call Calendar**
3. Click **Run workflow → Run workflow**

This populates the ICS file immediately without waiting for the daily schedule.

### Step 5 — Get your subscribe URL

Your calendar feed URL will be:

```
https://<your-github-username>.github.io/<your-repo-name>/jordan_oncall.ics
```

Example:
```
https://jordan.github.io/jordan-oncall-calendar/jordan_oncall.ics
```

### Step 6 — Subscribe in your calendar app

**Google Calendar:**
1. On the left sidebar, click **+** next to "Other calendars"
2. Choose **From URL**
3. Paste your URL and click **Add calendar**

**Apple Calendar (iPhone/Mac):**
1. Go to Settings → Calendar → Accounts → Add Account → Other
2. Tap **Add Subscribed Calendar**
3. Paste your URL

**Outlook:**
1. Go to Calendar → Add calendar → Subscribe from web
2. Paste your URL

---

The calendar updates once daily. Most calendar apps sync subscribed calendars every 24 hours.
