# Kingshot Gift Redeemer 🎁

An automated gift code redemption tool for Kingshot.net that processes bulk player IDs with a simple GUI interface. No login required, no hassle - just automation!

## ✨ Features

- **Bulk Redemption**: Process multiple player IDs in batches automatically
- **User-Friendly GUI**: Simple Tkinter interface for easy operation
- **Real-Time Logging**: Track redemption progress with detailed logs
- **Success/Failure Tracking**: Monitor successful and failed redemptions
- **Browser Automation**: Uses Playwright for reliable web automation
- **Batch Processing**: Processes IDs in groups of 3 for optimal performance
- **No Authentication Required**: Direct redemption without login

## 📋 Prerequisites

- Python 3.7 or higher
- Windows/Linux/macOS
- Internet connection

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

**IMPORTANT:** You must install the dependencies before running the script!

```bash
pip install -r requirements.txt
```

This will install the `playwright` library required for browser automation.

### 4. Install Playwright Browsers

After installing the Python package, you **MUST** install the browser binaries:

```bash
playwright install chromium
```

This will download the Chromium browser that Playwright uses for automation. This step is required and cannot be skipped!

### 5. Prepare Player IDs

Create or edit the `playerid.txt` file and add your player IDs (one per line):

```
86508749
87491467
84100109
```

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
   - Enter the gift code in the text field
   - Click "Start Redemption" button
   - Watch the progress in the log area
   - Wait for the completion message

### How It Works

1. The application reads all player IDs from `playerid.txt`
2. IDs are grouped into batches of 3
3. For each batch:
   - Opens the Kingshot bulk redemption page
   - Fills in the player IDs
   - Enters the gift code
   - Clicks the redeem button
   - Waits 8 seconds before processing the next batch
4. Displays a summary with success/failure counts

## 📁 Project Structure

```
kingshot_gift_redeemer/
├── gift_redeemer.py      # Main application script
├── playerid.txt          # Player IDs (one per line)
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── .gitignore           # Git ignore rules
```

## 🛠️ Technical Details

### Dependencies

- **playwright**: Browser automation library for web scraping and interaction
- **tkinter**: Built-in Python GUI library (no installation needed)

### Key Components

- **GiftRedeemerApp**: Main GUI application class
- **Threading**: Prevents UI freezing during redemption process
- **Playwright**: Handles browser automation and web interaction
- **Batch Processing**: Optimizes redemption with configurable batch sizes

## ⚠️ Important Notes

- The script processes IDs in batches of 3 (configurable in code, line 72)
- An 8-second delay is added between batches to avoid rate limiting
- The browser runs in non-headless mode so you can see the automation
- Make sure `playerid.txt` exists and contains valid player IDs
- Internet connection is required for the redemption process

## 🐛 Troubleshooting

### Virtual Environment Issues

If you can't activate the virtual environment:
- **Windows**: Try `python -m venv .venv` again
- **Linux/macOS**: Ensure you have `python3-venv` installed

### Playwright Browser Installation Errors

**Error: `playwright install chromium` fails or browser not found**

#### For All Platforms:
First, ensure playwright is installed:
```bash
pip list | grep playwright
```

If not installed, run:
```bash
pip install -r requirements.txt
```

Then try installing browsers again:
```bash
playwright install chromium
```

#### Linux-Specific Issues:

**1. Permission Denied Error:**
```bash
# Try with user permissions (recommended)
playwright install chromium

# If that fails, you may need sudo (use cautiously)
sudo playwright install chromium
```

**2. Missing System Dependencies:**
Ubuntu/Debian users may need additional libraries:
```bash
# Install required system dependencies
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2

# Then install chromium
playwright install chromium
```

For Fedora/RHEL/CentOS:
```bash
sudo dnf install -y \
    nss \
    nspr \
    atk \
    at-spi2-atk \
    cups-libs \
    libdrm \
    dbus-libs \
    libxkbcommon \
    libXcomposite \
    libXdamage \
    libXfixes \
    libXrandr \
    mesa-libgbm \
    pango \
    cairo \
    alsa-lib

playwright install chromium
```

**3. Command Not Found:**
If `playwright` command is not found, use the Python module directly:
```bash
python -m playwright install chromium
# OR
python3 -m playwright install chromium
```

#### macOS-Specific Issues:

**1. Command Not Found:**
Use the Python module directly:
```bash
python3 -m playwright install chromium
```

**2. Security/Quarantine Issues:**
macOS may block the browser. If you see security warnings:
```bash
# Install chromium
python3 -m playwright install chromium

# If blocked, allow it in System Preferences > Security & Privacy
# Or use this command to remove quarantine attribute:
xattr -cr ~/Library/Caches/ms-playwright/
```

**3. Rosetta 2 Required (Apple Silicon M1/M2/M3):**
If you're on Apple Silicon and get architecture errors:
```bash
# Install Rosetta 2 if not already installed
softwareupdate --install-rosetta

# Then install chromium
python3 -m playwright install chromium
```

#### Verification:

After installation, verify it worked:
```bash
# Check installed browsers
playwright install --help

# Or verify programmatically
python -c "from playwright.sync_api import sync_playwright; print('✓ Playwright ready!')"
```

### Module Not Found Errors

**Error: `ModuleNotFoundError: No module named 'playwright'`**

This means you haven't installed the dependencies yet. Follow these steps:

1. **Ensure virtual environment is activated**:
   - Windows: You should see `(.venv)` at the start of your command prompt
   - Linux/macOS: You should see `(.venv)` in your terminal prompt

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

4. **Verify installation**:
   ```bash
   pip list | grep playwright
   ```
   You should see `playwright` in the output.

If you still get errors, try:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### File Not Found: playerid.txt

Create the file in the same directory as `gift_redeemer.py`:
```bash
touch playerid.txt  # Linux/macOS
type nul > playerid.txt  # Windows
```

## 📊 Example Output

```
Found 102 IDs. Starting batch process...
Processing Batch 1/34 (3 IDs)...
Batch 1 Submitted Successfully! (3 IDs)
Current Stats - Success: 3, Failed: 0
Processing Batch 2/34 (3 IDs)...
Batch 2 Submitted Successfully! (3 IDs)
Current Stats - Success: 6, Failed: 0
...
==================================================
REDEMPTION SUMMARY
==================================================
Total IDs Processed: 102
✓ Successful: 102
✗ Failed: 0
==================================================
```

## 📝 License

This project is open source and available for personal use.

## 🤝 Contributing

Feel free to fork this repository and submit pull requests for improvements!

## ⚡ Quick Start Summary

```bash
# 1. Clone and navigate
git clone https://github.com/Ojas2005-git/kingshot_gift_redeemer.git
cd kingshot_gift_redeemer

# 2. Setup virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# OR
source .venv/bin/activate  # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 4. Add player IDs to playerid.txt

# 5. Run the application
python gift_redeemer.py
```

---

**Made with ❤️ for the Kingshot community**
