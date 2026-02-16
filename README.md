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

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

After installing the Python package, you need to install the browser binaries:

```bash
playwright install chromium
```

This will download the Chromium browser that Playwright uses for automation.

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

### Playwright Browser Not Found

If you get browser-related errors:
```bash
playwright install chromium
```

### Module Not Found Errors

Ensure you've activated the virtual environment and installed dependencies:
```bash
pip install -r requirements.txt
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
