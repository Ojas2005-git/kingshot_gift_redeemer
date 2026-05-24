# Kingshot Gift Redeemer 🎁

An automated gift code redemption tool for Kingshot.net that processes player IDs in parallel across 4 browser tabs inside a single browser window. No login required, no hassle - just automation!

## 🆕 What's New in v2

> **Important:** Kingshot.net has discontinued bulk gift code redemption at the request of Century Games (the Kingshot publisher). Version 2 switches to the new **one-by-one redemption** flow using `https://kingshot.net/gift-codes/redeem`, running across **4 parallel browser tabs** inside a single browser window.

| Feature | v1 (Old) | v2 (Current) |
|---|---|---|
| Redemption URL | `/gift-codes/bulk-redeem` ❌ (discontinued) | `/gift-codes/redeem` ✅ |
| Processing style | Parallel batches of 3 IDs | 4 tabs in one browser, each processing its chunk in parallel |
| Player lookup | Not required | **Lookup Player** step before redeem |
| Browser windows | Up to 10 separate windows | **1 browser window, 4 tabs** |
| Stop mid-run | ❌ | ✅ Stop button (halts all tabs after current player) |
| Outcome categories | Success / Failed | Success / Skipped / Already Redeemed / Error |
| Failed ID list | ❌ | ✅ Printed in per-tab and overall summary |
| UI theme | Default grey | Dark theme with 4-tab notebook (Catppuccin-inspired) |

---

## ✨ Features

- **4-Tab Parallel Processing**: Splits player IDs across 4 browser tabs in a single browser window — ~4× faster than sequential
- **Smart ID Splitting**: First 3 tabs get equal shares; Tab 4 always absorbs any remainder (odd counts handled automatically)
- **Player Lookup Validation**: Automatically checks if a player exists before attempting redemption
- **Stop Button**: Gracefully halts all 4 tabs after their current player finishes
- **Per-Tab Live Logs**: Each tab has its own colour-coded log panel in the GUI notebook
- **Detailed Outcome Tracking**: Tracks Success, Skipped (not found), Already Redeemed, and Error per tab and overall
- **Failed ID Report**: Prints all failed/not-found player IDs at the end of each tab and in the combined summary
- **Browser Automation**: Uses Playwright — one browser, one context, 4 pages
- **No Authentication Required**: Direct redemption without login

---

## 📋 Prerequisites

- Python 3.7 or higher
- Windows / Linux / macOS
- Internet connection

---

## 🚀 Setup Guide

### 1. Clone the Repository

```bash
git clone https://github.com/Ojas2005-git/kingshot_gift_redeemer.git
cd kingshot_gift_redeemer
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

```bash
playwright install chromium
```

This downloads the Chromium browser used for automation. This step is **required** and cannot be skipped.

### 5. Prepare Player IDs

Edit `playerid.txt` and add your player IDs — one per line:

```
86508749
87491467
84100109
```

---

## 📖 Usage

### Running the Application

1. **Activate the virtual environment** (if not already activated):
   - Windows: `.venv\Scripts\activate`
   - Linux/macOS: `source .venv/bin/activate`

2. **Run the script**:
   ```bash
   python gift_redeemer.py
   ```

3. **Use the GUI**:
   - Enter the gift code in the **Gift Code** field
   - Click **▶ Start Redemption**
   - Watch colour-coded progress in the log area
   - Use **⏹ Stop** at any time to pause after the current player
   - A summary popup appears when all IDs have been processed

### How It Works (v2 Flow)

On **Start**, the script:

1. Reads all player IDs from `playerid.txt`
2. Splits them into **4 chunks** — first 3 tabs get `floor(total ÷ 4)` IDs each, Tab 4 gets the rest
3. Launches **one Chromium browser window** with **4 tabs** opened simultaneously
4. All 4 tabs run in parallel via `asyncio.gather`. For each player ID in its chunk, a tab:
   - Opens `https://kingshot.net/gift-codes/redeem`
   - Fills in the **Player ID** and clicks **Lookup Player**
   - If player not found → logs as Skipped, moves to next ID
   - If player found → fills the **Gift Code** and clicks **Redeem Gift Code**
   - Parses the server response and logs the outcome
   - Waits 1.5 seconds before the next player
5. When all 4 tabs finish, a combined summary is shown

**Example split for 103 player IDs:**

| Tab | Player IDs assigned |
|-----|---------------------|
| Tab 1 | 25 (IDs #1–25) |
| Tab 2 | 25 (IDs #26–50) |
| Tab 3 | 25 (IDs #51–75) |
| Tab 4 | **28** (IDs #76–103, absorbs remainder) |

---

## 📁 Project Structure

```
kingshot_gift_redeemer/
├── gift_redeemer.py      # Main application script (v2)
├── playerid.txt          # Player IDs (one per line)
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── .gitignore            # Git ignore rules
```

---

## 🛠️ Technical Details

### Dependencies

- **playwright**: Browser automation library
- **tkinter**: Built-in Python GUI library (no installation needed)

### Key Components

| Component | Description |
|---|---|
| `GiftRedeemerApp` | Main GUI class — manages UI state and background thread |
| `redeem_for_player()` | Async function handling the full lookup + redeem flow for one player on a given page |
| `tab_worker()` | Async task for one browser tab — iterates over its chunk of player IDs |
| `run_redemption_async()` | Orchestrator — splits IDs, opens 1 browser + 4 pages, launches 4 parallel `tab_worker` tasks |
| `run_redemption()` | Thread entry point — runs the async loop without blocking the UI |

### Outcome States

| State | Meaning |
|---|---|
| ✅ `success` | Gift code redeemed successfully |
| `~` `not_found` | Player ID not found on server (ID listed in summary) |
| `~` `already_redeemed` | Code was already claimed for this player |
| ✗ `error` | Page/network issue (ID listed in summary) |
| ✗ `invalid_code` | Gift code is invalid/expired — **run stops immediately** |

---

## ⚠️ Important Notes

- **One browser window** opens with **4 tabs** — all tabs are visible and run simultaneously
- A **1.5-second delay** is added between each player *per tab* to avoid rate limiting
- If the gift code is **invalid or expired**, the affected tab stops early — other tabs continue
- Player IDs that don't exist on the server are **skipped** and listed in the final summary
- Tab 4 always receives any remainder IDs (e.g. for 103 IDs: Tab 4 gets 28, others get 25 each)
- Make sure `playerid.txt` exists in the same directory as `gift_redeemer.py`

---

## 📊 Example Output (v2)

Each of the 4 GUI tabs shows its own live log. Example from **Tab 1**:

```
═══ Tab 1 ═══  (25 players)
Assigned 25 players  (IDs #1–25)

[1/25] Processing: 86508749
  ✓ [86508749] SUCCESSFUL.

[2/25] Processing: 87491467
  – [87491467] Player not found on server.

[3/25] Processing: 84100109
  ~ [84100109] Code already redeemed (skipped).

...

── Tab Summary ──
  ✓ Success : 22
  ~ Skipped : 2
  ✗ Failed  : 1
```

At the end, the **overall summary** is appended to all 4 tabs:

```
═══════════════  OVERALL SUMMARY  ═══════════════
  Total Players  : 103
  ✓ Successful   : 90
  ~ Skipped      : 10
  ✗ Failed/Error : 3

  Player IDs that failed / not found:
    • 87491467
    • 84100109
    • ...
══════════════════════════════════════════════════
```

---

## 🐛 Troubleshooting

### Playwright Browser Installation Errors

**Error: `playwright install chromium` fails or browser not found**

First verify playwright is installed:
```bash
pip list | grep playwright
```

If missing:
```bash
pip install -r requirements.txt
playwright install chromium
```

#### Linux-Specific Issues

**Missing System Dependencies (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libdbus-1-3 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libpango-1.0-0 libcairo2 libasound2

playwright install chromium
```

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install -y nss nspr atk at-spi2-atk cups-libs libdrm \
    dbus-libs libxkbcommon libXcomposite libXdamage libXfixes \
    libXrandr mesa-libgbm pango cairo alsa-lib

playwright install chromium
```

**Command Not Found:**
```bash
python -m playwright install chromium
```

#### macOS-Specific Issues

**Security/Quarantine Issues:**
```bash
python3 -m playwright install chromium
xattr -cr ~/Library/Caches/ms-playwright/   # if blocked by macOS security
```

**Apple Silicon (M1/M2/M3):**
```bash
softwareupdate --install-rosetta
python3 -m playwright install chromium
```

### Module Not Found Errors

**`ModuleNotFoundError: No module named 'playwright'`**

1. Ensure the virtual environment is active (`(.venv)` visible in your prompt)
2. Run: `pip install -r requirements.txt`
3. Run: `playwright install chromium`
4. Verify: `pip list | grep playwright`

### File Not Found: playerid.txt

```bash
touch playerid.txt          # Linux/macOS
type nul > playerid.txt     # Windows
```

---

## ⚡ Quick Start Summary

```bash
# 1. Clone and navigate
git clone https://github.com/Ojas2005-git/kingshot_gift_redeemer.git
cd kingshot_gift_redeemer

# 2. Setup virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# OR
source .venv/bin/activate    # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 4. Add player IDs to playerid.txt (one per line)

# 5. Run the application
python gift_redeemer.py
```

---

## 📝 License

This project is open source and available for personal use.

## 🤝 Contributing

Feel free to fork this repository and submit pull requests for improvements!

---

**Made with ❤️ for the Kingshot community**
