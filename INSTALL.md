# Upwork Bid Tracker — A to Z Installation Guide

This guide takes you from zero to a fully working module installed on both your
local Community instance and your production Enterprise instance.

> **Time required:** 30-60 minutes for first install, including troubleshooting.

---

## Table of Contents

1. [What you're installing](#1-what-youre-installing)
2. [Prerequisites](#2-prerequisites)
3. [Compatibility note: version of Odoo](#3-compatibility-note-version-of-odoo)
4. [Phase A — Local Community install](#4-phase-a--local-community-install-test-here-first)
5. [Phase B — Production Enterprise install](#5-phase-b--production-enterprise-install)
6. [Phase C — Post-install configuration](#6-phase-c--post-install-configuration)
7. [Phase D — Test checklist](#7-phase-d--test-checklist-run-this-end-to-end)
8. [Troubleshooting](#8-troubleshooting)
9. [How to make changes later](#9-how-to-make-changes-later)
10. [Appendix: file inventory](#10-appendix-file-inventory)

---

## 1. What you're installing

A custom Odoo module called `upwork_bid_tracker` that adds an **Upwork Bids**
app to your Odoo with:

- **Kanban board** organized by stage (Draft → Submitted → Viewed → Replied → Interview → Moved to CRM / No Response / Won / Lost).
- **Three-tab form** for each bid:
  1. **Job & Client** — job details + client profile data.
  2. **Proposal** — what we quoted, including our budget separate from client's.
  3. **Business Dev** — tracking dates, bidder, outcome.
- **Five profiles seeded:** Awais, Zain Ali, Wahab (plus you can add more).
- **One-click "Convert to CRM"** button that creates a `crm.lead` and links back.
- **Computed budget variance** (Our Bid − Client Budget).
- **Auto-archive cron** for stale bids (no activity for 14 days).
- **Three permission groups:** Bidder, Team Lead, Manager.

---

## 2. Prerequisites

| Item | Required for | Notes |
|---|---|---|
| Odoo Community installed locally | Phase A | You said you've done this. |
| Odoo Enterprise running in production | Phase B | At `odoo.odobridge.com`. |
| Python 3.10+ | Both | Comes with Odoo; nothing to install. |
| Server access to production | Phase B | SSH/SFTP or hosting provider support. |
| CRM module installed in Odoo | Both | Required dependency. We auto-install it. |
| HR module installed in Odoo | Both | Required dependency. |

If `crm` and `hr` are not installed yet, Odoo will install them automatically
when you install this module — they're declared in the `depends` list.

---

## 3. Compatibility note: version of Odoo

This module's manifest declares version `17.0.1.0.0`. The view syntax used
(`<list>` instead of `<tree>`, `<chatter/>` shorthand, `invisible="..."`
attributes instead of `attrs={}`) is **compatible with Odoo 17, 18, and 19**.

**Before you start, confirm your local and production versions match:**

```bash
# On your local Odoo (Community)
odoo-bin --version
# Or in the Odoo UI: Settings → look at version in bottom-right
```

If your **local is 17/18 and production is 19** (or vice versa), the module
should still install — but test thoroughly on the production-matching version.
If versions differ wildly (e.g. one is 16), tell me and I'll adjust the
manifest version string.

---

## 4. Phase A — Local Community install (TEST HERE FIRST)

**Never install a brand-new module straight into production. Always test locally.**

### Step A1 — Find your local addons path

On your local Odoo install, find the `odoo.conf` file. Common locations:

| OS | Typical path |
|---|---|
| Windows | `C:\Program Files\Odoo 17.x\server\odoo.conf` |
| macOS | `/Applications/Odoo.app/Contents/server/odoo.conf` |
| Linux (apt) | `/etc/odoo/odoo.conf` |
| Linux (manual) | wherever you put it |
| Docker | Inside the container; check `docker inspect` for the mount point |

Open it and look for the `addons_path` line:

```
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/opt/odoo/custom-addons
```

The **last comma-separated entry** is usually your custom addons folder.
If only the default path is listed, you'll need to create a custom folder
and add it.

**If you don't have a custom addons folder yet:**

```bash
# Create one (Linux/macOS)
sudo mkdir -p /opt/odoo/custom-addons
sudo chown -R $USER:$USER /opt/odoo/custom-addons
```

Then edit `odoo.conf`:
```
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/opt/odoo/custom-addons
```

On Windows, pick a folder like `C:\odoo-addons` and add it the same way.

### Step A2 — Copy the module folder into addons path

Copy the **entire `upwork_bid_tracker/` folder** (the one containing
`__manifest__.py`) into your custom addons path:

```bash
# Linux/macOS
cp -r /path/to/upwork_bid_tracker /opt/odoo/custom-addons/

# Verify
ls /opt/odoo/custom-addons/upwork_bid_tracker
# You should see: __init__.py  __manifest__.py  models/  views/  ...
```

```powershell
# Windows PowerShell
Copy-Item -Recurse C:\Downloads\upwork_bid_tracker C:\odoo-addons\
```

### Step A3 — Restart your local Odoo

The restart is needed so Odoo notices the new folder.

```bash
# Linux systemd
sudo systemctl restart odoo

# Linux manual
# Stop the running process (Ctrl+C in its terminal), then:
./odoo-bin -c /etc/odoo/odoo.conf

# Windows
# Services → Odoo → Restart
# Or: net stop odoo-server-17.0 && net start odoo-server-17.0

# macOS
# Quit Odoo from the menu bar icon, then re-open the app
```

### Step A4 — Update Apps List and install

1. Open your local Odoo in browser (typically `http://localhost:8069`).
2. **Enable Developer Mode:** Settings → Developer Tools → "Activate Developer Mode".
3. Go to the **Apps** menu.
4. **Click the "Update Apps List" button at the top** (only visible in Dev Mode).
   In the popup, click "Update".
5. **Remove the "Apps" filter** in the search bar (it filters to only certified apps;
   yours isn't certified).
6. Search: `Upwork Bid Tracker`.
7. Click **Install**.

If install succeeds → skip to Phase C.
If install fails → see [Troubleshooting](#8-troubleshooting).

---

## 5. Phase B — Production Enterprise install

**Only do this after Phase A works perfectly.**

### Step B1 — Identify your production addons path

Three ways to find it depending on your hosting setup:

**If you have SSH access to the server:**
```bash
ssh user@odoo.odobridge.com
sudo cat /etc/odoo/odoo.conf | grep addons_path
```

**If hosted on a managed platform (likely the case for odobridge.com):**
Contact their support and ask:
- "What is the path for custom addons?"
- "Can I upload a custom module via SFTP, or do you have a deployment process?"

**If on Odoo.sh:**
Custom addons go in the linked Git repository; pushing to the branch
auto-deploys.

### Step B2 — Get the module onto the server

Pick **one** method based on what your hosting supports:

#### Method 1: SFTP/SCP (most flexible)
```bash
# From your local machine
scp -r upwork_bid_tracker/ user@odoo.odobridge.com:/path/to/custom-addons/
```

#### Method 2: Git (best for ongoing changes)
```bash
# Create a private Git repo, push the module to it, then on the server:
ssh user@odoo.odobridge.com
cd /path/to/custom-addons
git clone https://github.com/yourorg/upwork_bid_tracker.git
```

#### Method 3: Hosting provider upload
Some managed hosts (Odoo.sh and similar) let you upload modules through their
admin panel. Check with odobridge.com support.

#### Method 4: Zip and ask support to install
```bash
# Locally
cd /path/where/the/module/folder/lives
zip -r upwork_bid_tracker.zip upwork_bid_tracker/
```
Email the zip to your hosting provider's support, asking them to extract it
into the custom addons folder and restart Odoo.

### Step B3 — Restart production Odoo

If you did the copy yourself with SSH:
```bash
sudo systemctl restart odoo
```

If managed: ask the provider to restart, or use their admin panel's restart
button if one exists.

### Step B4 — Install via the production Apps menu

1. Log into production Odoo as administrator.
2. Enable Developer Mode (Settings → Developer Tools).
3. Apps → Update Apps List → Update.
4. Remove the "Apps" filter, search "Upwork Bid Tracker", click Install.

---

## 6. Phase C — Post-install configuration

You'll need to do these one-time setup steps after install.

### C1 — Assign users to permission groups

The module creates three groups. Every user who needs the app must be in at
least one of them.

1. Settings → Users & Companies → Users.
2. Open a user.
3. Find the "Upwork Bids" section in the access rights.
4. Set their role:
   - **Bidder** — can create/edit/see only their own bids.
   - **Team Lead** — can see and edit all bids; manages profiles/templates/stages.
   - **Manager** — same as Team Lead plus reporting (currently same access).
5. Save.

Repeat for every team member. You'll need to give yourself **Manager** to do
the rest of the setup.

### C2 — Verify seed data loaded

Go to **Upwork Bids → Configuration**:

- **Stages** → should show 9 stages from "Draft / To Bid" to "Lost".
- **Upwork Profiles** → should show Awais, Zain Ali, Wahab.

If anything is missing, the data files didn't load. Try uninstalling and
reinstalling the module.

### C3 — Customize profiles for your team

For each of Awais / Zain / Wahab (and add more for your other bidders):
1. Configuration → Upwork Profiles → click the profile.
2. Fill in: Upwork Username, Profile URL, Default Bidder (link to their HR
   employee record), Connects Balance, Default Hourly Rate.
3. Save.

### C4 — Optional: add common skill tags

Configuration → Skill Tags → New. Add tags your team uses often:
React, Node.js, Python, Figma, n8n, Flutter, etc.

For each skill, optionally link it to a **CRM Tag** — when a bid is converted
to CRM, this tag gets applied to the opportunity. Useful for CRM filtering.

### C5 — Optional: add cover letter templates

Configuration → Cover Letter Templates → New. Paste your team's best-performing
templates. They'll be selectable on every new bid.

---

## 7. Phase D — Test checklist (run this end-to-end)

Before letting the team use it, validate the whole flow yourself:

| # | Test | Expected result |
|---|---|---|
| 1 | Open Upwork Bids → My Bids | Empty kanban with stage columns visible |
| 2 | Create a new bid: title "Test bid", profile = Zain Ali | Saves cleanly |
| 3 | Fill Tab 1: client_budget = 1000, all client fields | Saves |
| 4 | Fill Tab 2: proposed_budget = 1200, connects_used = 4 | budget_variance shows 200 |
| 5 | Fill Tab 3: submitted_date now, outcome = pending | Saves |
| 6 | Drag the kanban card from "Submitted" to "Replied" | Stage updates |
| 7 | Click "Convert to CRM" in the form header | New CRM opportunity opens |
| 8 | In the CRM opportunity, verify: name, partner, expected revenue, salesperson, link back to the bid | All present |
| 9 | Go back to the bid | Stage = "Moved to CRM", green badge "In CRM" on card |
| 10 | Try to click "Convert to CRM" again | Error "Already linked to..." |
| 11 | Log in as a Bidder user; create a bid; log out | Saves |
| 12 | Log in as a different Bidder | Does NOT see the other bidder's bid |
| 13 | Log in as Team Lead | Sees both bids |
| 14 | List view → multi-select bids → bulk edit | Works |
| 15 | Pivot view → grouped by Profile × Outcome | Renders |

If all 15 pass — you're done. Hand off to the team.

---

## 8. Troubleshooting

### "Module not found" after Update Apps List

- Check the folder is **directly inside** the addons path. The path should be
  `<addons_path>/upwork_bid_tracker/__manifest__.py`, NOT
  `<addons_path>/something/upwork_bid_tracker/__manifest__.py`.
- Check **read permissions** — the Odoo system user must be able to read the
  folder:
  ```bash
  sudo chown -R odoo:odoo /opt/odoo/custom-addons/upwork_bid_tracker
  sudo chmod -R 755 /opt/odoo/custom-addons/upwork_bid_tracker
  ```
- Confirm `addons_path` in `odoo.conf` actually contains your custom folder.
- Restart Odoo. Without a restart, new module folders are invisible.

### "Invalid view definition" or XML error during install

Almost always a version mismatch. Check the error message — Odoo tells you
which view file and roughly which element. Most common causes:
- `<list>` tag in Odoo 16 → rename to `<tree>` everywhere.
- `<chatter/>` shorthand in Odoo 16 → replace with old chatter block.
- `invisible="..."` attribute syntax in Odoo 16 → use `attrs="{'invisible': [...]}"`.

If your local is 16, ping me — I'll downgrade the view files.

### Install fails on "crm.lost.reason" model

Either the CRM module didn't auto-install, or your Odoo version uses a
slightly different name. Try:
1. Apps → install "CRM" manually first.
2. Then install "Upwork Bid Tracker".

### "Permission denied" when opening the app menu

You haven't assigned yourself to any Upwork group yet. The menus require at
least **Bidder** access. Go to Settings → Users → yourself → assign yourself
Manager.

### Kanban shows but no cards / drag-and-drop doesn't work

Open browser DevTools (F12) → Console → look for JS errors. Most common cause
is browser cache holding old assets. Hard refresh: Ctrl+Shift+R (Cmd+Shift+R
on Mac), or open in an Incognito window.

### "Convert to CRM" button does nothing

- Check `upwork_profile_id` is filled — it's required for the bid to save
  cleanly, and the conversion logic doesn't run if the record isn't saved.
- Open browser DevTools → Network tab → click the button again → look for the
  failed request and inspect the error response.
- Check Odoo server logs:
  ```bash
  sudo journalctl -u odoo -n 100 --no-pager
  # Or: tail -f /var/log/odoo/odoo-server.log
  ```

### "psycopg2.errors.UniqueViolation: duplicate key"

The SQL constraint blocks duplicate bids for the same job URL + profile
combination. If you genuinely want to bid the same job from the same profile
twice, edit `models/upwork_bid.py` and remove the `_sql_constraints` block,
then upgrade the module.

---

## 9. How to make changes later

### To add a field

**Option 1 — quick, no developer:** Studio. Open any bid → click 🎨 Studio →
add field. The field will be prefixed `x_` (e.g. `x_my_new_field`). Studio
saves changes to a separate auto-generated module, so it won't conflict with
this one.

**Option 2 — proper, version-controlled:** Edit the relevant model file,
add the field. Edit the relevant view file, place the field. Upgrade the
module: Apps → search "Upwork Bid Tracker" → click "Upgrade".

### To upgrade after code changes

1. Replace the files on the server.
2. Apps → search the module → click **Upgrade** (not Install — Install only
   works for not-yet-installed modules).
3. Wait ~30 seconds.
4. Hard-refresh your browser to clear cached UI assets.

### To uninstall

Apps → search the module → click Uninstall.

⚠️ **This deletes all bid data.** Export your data first if you want to keep it:
Upwork Bids → list view → select all → ⚙️ Actions menu → Export.

---

## 10. Appendix: file inventory

The module contains 24 files:

```
upwork_bid_tracker/
├── __init__.py
├── __manifest__.py
├── data/
│   ├── upwork_bid_stage_data.xml      ← seeds 9 default stages
│   ├── upwork_profile_data.xml        ← seeds Awais, Zain, Wahab
│   └── upwork_sequence_data.xml       ← BID/YYYY/NNNNN numbering
├── models/
│   ├── __init__.py
│   ├── crm_lead.py                    ← adds upwork_bid_id back-reference
│   ├── upwork_bid.py                  ← main model (~430 lines, most of the logic)
│   ├── upwork_bid_stage.py
│   ├── upwork_category.py
│   ├── upwork_cover_template.py
│   ├── upwork_profile.py              ← Awais/Zain/Wahab model
│   └── upwork_skill_tag.py
├── security/
│   ├── ir.model.access.csv            ← model-level access per group
│   ├── upwork_record_rules.xml        ← Bidder sees own only / Lead sees all
│   └── upwork_security.xml            ← defines Bidder/Lead/Manager groups
├── static/
│   └── description/
│       └── icon.png                   ← module icon shown in Apps list
└── views/
    ├── crm_lead_views.xml             ← adds bid link to CRM form
    ├── menus.xml                      ← Upwork Bids → Bids / Configuration tree
    ├── upwork_bid_stage_views.xml
    ├── upwork_bid_views.xml           ← main kanban + 3-tab form + list + pivot + graph + calendar + search + cron
    ├── upwork_category_views.xml
    ├── upwork_cover_template_views.xml
    ├── upwork_profile_views.xml
    └── upwork_skill_tag_views.xml
```

You're holding a complete, working Odoo module. Welcome to Odoo development.
