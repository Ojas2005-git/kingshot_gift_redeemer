import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
from playwright.sync_api import sync_playwright
import os
import time

class GiftRedeemerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gift Code Redeemer")
        self.root.geometry("600x400")

        # Gift Code Input
        self.code_label = tk.Label(root, text="Enter Gift Code:", font=("Arial", 12))
        self.code_label.pack(pady=10)

        self.code_entry = tk.Entry(root, font=("Arial", 12), width=30)
        self.code_entry.pack(pady=5)

        # Start Button
        self.start_button = tk.Button(root, text="Start Redemption", font=("Arial", 12, "bold"), 
                                      bg="#4CAF50", fg="white", command=self.start_process)
        self.start_button.pack(pady=20)

        # Log Area
        self.log_area = scrolledtext.ScrolledText(root, width=70, height=15, font=("Courier", 10))
        self.log_area.pack(pady=10)

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def safe_log(self, message):
        """Schedule the log update on the main thread."""
        self.root.after(0, lambda: self.log(message))

    def safe_showinfo(self, title, message):
        """Schedule the messagebox on the main thread."""
        self.root.after(0, lambda: messagebox.showinfo(title, message))

    def start_process(self):
        code = self.code_entry.get().strip()
        if not code:
            messagebox.showwarning("Input Error", "Please enter a gift code.")
            return

        self.start_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.run_redemption, args=(code,))
        thread.start()

    def run_redemption(self, gift_code):
        player_file = "playerid.txt"
        
        if not os.path.exists(player_file):
            self.safe_log(f"Error: {player_file} not found!")
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            return

        try:
            with open(player_file, "r") as f:
                ids = [line.strip() for line in f if line.strip()]
            
            if not ids:
                self.safe_log("Error: No IDs found in file.")
                self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
                return

            self.safe_log(f"Found {len(ids)} IDs. Starting batch process...")

            # Batch IDs into groups of 3 (User preferred)
            batches = [ids[i:i + 3] for i in range(0, len(ids), 3)]

            # Initialize success and failure counters
            success_count = 0
            failed_count = 0

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()

                for i, batch in enumerate(batches):
                    self.safe_log(f"Processing Batch {i + 1}/{len(batches)} ({len(batch)} IDs)...")
                    
                    try:
                        page.goto("https://kingshot.net/gift-codes/bulk-redeem")
                        
                        # Fill Account IDs
                        ids_text = "\n".join(batch)
                        page.fill("#account-ids", ids_text)
                        
                        # Fill Gift Code
                        page.fill("#gift-code", gift_code)
                        
                        # Click Redeem
                        page.click("button.bg-primary.w-full")
                        
                        # Batch succeeded
                        success_count += len(batch)
                        self.safe_log(f"Batch {i + 1} Submitted Successfully! ({len(batch)} IDs)")
                        self.safe_log(f"Current Stats - Success: {success_count}, Failed: {failed_count}")
                        
                        # Wait for a bit to ensure submission is registered
                        time.sleep(8)
                        
                    except Exception as e:
                        # Batch failed
                        failed_count += len(batch)
                        self.safe_log(f"Error in batch {i + 1}: {str(e)}")
                        self.safe_log(f"Current Stats - Success: {success_count}, Failed: {failed_count}")

                browser.close()
            
            self.safe_log("=" * 50)
            self.safe_log("REDEMPTION SUMMARY")
            self.safe_log("=" * 50)
            self.safe_log(f"Total IDs Processed: {len(ids)}")
            self.safe_log(f"✓ Successful: {success_count}")
            self.safe_log(f"✗ Failed: {failed_count}")
            self.safe_log("=" * 50)
            self.safe_showinfo("Completed", f"Redemption process completed!\n\nSuccessful: {success_count}\nFailed: {failed_count}")

        except Exception as e:
            self.safe_log(f"Critical Error: {str(e)}")
        
        finally:
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    app = GiftRedeemerApp(root)
    root.mainloop()
