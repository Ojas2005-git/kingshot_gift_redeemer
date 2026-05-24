# Kingshot Gift Redeemer 🎁

An automated gift code redemption tool for Kingshot.net that processes player IDs one-by-one with a simple GUI interface. No login required, no hassle - just automation!

## 🆕 What's New in v2

> **Important:** Kingshot.net has discontinued bulk gift code redemption at the request of Century Games (the Kingshot publisher). Version 2 switches to the new **one-by-one redemption** flow using `https://kingshot.net/gift-codes/redeem`.

| Feature | v1 (Old) | v2 (Current) |
|---|---|---|
| Redemption URL | `/gift-codes/bulk-redeem` ❌ (discontinued) | `/gift-codes/redeem` ✅ |
| Processing style | Parallel batches of 3 IDs | One player at a time |
| Player lookup | Not required | **Lookup Player** step before redeem |
| Stop mid-run | ❌ | ✅ Stop button |
| Outcome categories | Success / Failed | Success / Skipped / Already Redeemed / Error |
| Failed ID list | ❌ | ✅ Printed in summary |
| UI theme | Default grey | Dark theme (Catppuccin-inspired) |

---

## ✨ Features

- **One-by-One Redemption**: Processes each player ID individually through the official redeem page
- **Player Lookup Validation**: Automatically checks if a player exists before attempting redemption
- **Stop Button**: Gracefully halt the run after the current player finishes
- **Dark UI**: Colour-coded log lines (green = success, red = fail, yellow = warnings/skipped)
- **Detailed Outcome Tracking**: Tracks Success, Skipped (not found), Already Redeemed, and Error states
- **Failed ID Report**: Prints all failed/not-found player IDs at the end of the run
- **Browser Automation**: Uses Playwright for reliable web automation
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

For **each** player ID in `playerid.txt`, the script:

1. Opens `https://kingshot.net/gift-codes/redeem`
2. Fills in the **Player ID** field and clicks **Lookup Player**
3. Checks the result:
   - **Player not found** → logs as Skipped, moves to the next ID
   - **Player found** → scrolls to the Gift Code section
4. Fills in the **Gift Code** and clicks **Redeem Gift Code**
5. Parses the server response and logs the outcome
6. Waits 1.5 seconds before moving to the next player

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
| `redeem_for_player()` | Async function handling the full lookup + redeem flow for one player |
| `run_redemption_async()` | Orchestrates sequential processing of all player IDs |
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

- A **1.5-second delay** is added between each player to avoid rate limiting
- The browser runs in **non-headless mode** so you can watch the automation live
- If the gift code is **invalid or expired**, the run stops early to avoid wasted requests
- Player IDs that don't exist on the server are **skipped** and listed in the final summary
- Make sure `playerid.txt` exists in the same directory as `gift_redeemer.py`

---

## 📊 Example Output (v2)

```
═══════════════════════════════════════════════
  Kingshot Gift Code Redeemer — One-by-One
  Gift Code : EXAMPLE123
  Players   : 103
═══════════════════════════════════════════════

[1/103] Processing player: 86508749
  ✓ [86508749] Redemption SUCCESSFUL.

[2/103] Processing player: 87491467
  – [87491467] Player not found on server.

[3/103] Processing player: 84100109
  ~ [84100109] Code already redeemed (skipped).

...

═══════════════════════════════════════════════
  REDEMPTION SUMMARY
═══════════════════════════════════════════════
  Total Players  : 103
  ✓ Successful   : 98
  ~ Skipped      : 4
  ✗ Failed/Error : 1

  Player IDs that failed / not found:
    • 87491467
    • 84100109
    • ...
═══════════════════════════════════════════════
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
