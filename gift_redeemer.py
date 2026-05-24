import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import asyncio
import os
import time
from queue import Queue
from threading import Lock

class GiftRedeemerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gift Code Redeemer - Parallel Processing")
        self.root.geometry("700x500")

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
        self.log_area = scrolledtext.ScrolledText(root, width=80, height=20, font=("Courier", 9))
        self.log_area.pack(pady=10)

        # Thread-safe counters
        self.success_count = 0
        self.failed_count = 0
        self.counter_lock = Lock()

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def safe_log(self, message):
        """Schedule the log update on the main thread."""
        self.root.after(0, lambda: self.log(message))

    def safe_showinfo(self, title, message):
        """Schedule the messagebox on the main thread."""
        self.root.after(0, lambda: messagebox.showinfo(title, message))

    def increment_success(self, count):
        """Thread-safe success counter increment."""
        with self.counter_lock:
            self.success_count += count

    def increment_failed(self, count):
        """Thread-safe failed counter increment."""
        with self.counter_lock:
            self.failed_count += count

    def start_process(self):
        code = self.code_entry.get().strip()
        if not code:
            messagebox.showwarning("Input Error", "Please enter a gift code.")
            return

        self.start_button.config(state=tk.DISABLED)
        # Reset counters
        self.success_count = 0
        self.failed_count = 0
        
        thread = threading.Thread(target=self.run_redemption, args=(code,))
        thread.start()

    async def process_batch_with_retry(self, page, batch, batch_num, gift_code, max_retries=3):
        """Process a single batch with retry logic and server response waiting."""
        task_name = asyncio.current_task().get_name()
        for attempt in range(max_retries):
            try:
                self.safe_log(f"[{task_name}] Processing Batch #{batch_num} (Attempt {attempt + 1}/{max_retries})")
                
                # Navigate to the page
                try:
                    await page.goto("https://kingshot.net/gift-codes/bulk-redeem", timeout=30000)
                except Exception as e:
                    self.safe_log(f"[{task_name}] Batch #{batch_num} - Navigation Error: {str(e)}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(3)
                        continue
                    return False
                
                # Fill Account IDs
                ids_text = "\n".join(batch)
                await page.fill("#account-ids", ids_text)
                
                # Fill Gift Code
                await page.fill("#gift-code", gift_code)
                
                # Click Redeem
                await page.click("button.bg-primary.w-full")
                
                # Wait for server response - using a broad selector for any feedback
                try:
                    await page.wait_for_selector(
                        "div.alert, div.notification, div.message, div.toast, div.result, .success, .error, .text-red, .text-green",
                        timeout=60000,
                        state="visible"
                    )
                    
                    await asyncio.sleep(2)
                    
                    # Check for errors
                    error_selectors = [".error", ".alert-error", ".text-red", "[class*='error']"]
                    has_error = False
                    for selector in error_selectors:
                        if await page.locator(selector).count() > 0:
                            if await page.locator(selector).first.is_visible():
                                error_text = await page.locator(selector).first.text_content(timeout=1000)
                                if error_text and len(error_text.strip()) > 0:
                                    self.safe_log(f"[{task_name}] Batch #{batch_num} - Server Error: {error_text[:100]}")
                                    has_error = True
                                    break
                    
                    if has_error:
                        if attempt < max_retries - 1:
                            self.safe_log(f"[{task_name}] Retrying Batch #{batch_num}...")
                            await asyncio.sleep(3)
                            continue
                        else:
                            self.increment_failed(len(batch))
                            self.safe_log(f"[{task_name}] Batch #{batch_num} FAILED after {max_retries} attempts")
                            return False
                    
                    # Success!
                    self.increment_success(len(batch))
                    self.safe_log(f"[{task_name}] Batch #{batch_num} SUCCESS! ({len(batch)} IDs)")
                    return True
                    
                except PlaywrightTimeoutError:
                    self.safe_log(f"[{task_name}] Batch #{batch_num} - Server response timeout")
                    if attempt < max_retries - 1:
                        self.safe_log(f"[{task_name}] Retrying Batch #{batch_num}...")
                        await asyncio.sleep(5)
                        continue
                    else:
                        self.increment_failed(len(batch))
                        self.safe_log(f"[{task_name}] Batch #{batch_num} FAILED - Server timeout")
                        return False
                        
            except Exception as e:
                self.safe_log(f"[{task_name}] Batch #{batch_num} Error: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(3)
                    continue
                else:
                    self.increment_failed(len(batch))
                    return False
        
        return False

    async def tab_worker(self, browser, queue, gift_code):
        """Async worker function for each browser tab."""
        task_name = asyncio.current_task().get_name()
        
        # Create separate context/page for this task
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            while True:
                try:
                    # Get batch from queue (async non-blocking)
                    batch_data = queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
                
                batch_num, batch = batch_data
                await self.process_batch_with_retry(page, batch, batch_num, gift_code)
                
                queue.task_done()
                
                # Small delay between batches
                await asyncio.sleep(2)
                    
        finally:
            await page.close()
            await context.close()
            self.safe_log(f"[{task_name}] Closed")

    async def run_redemption_async(self, gift_code):
        player_file = "playerid.txt"
        
        if not os.path.exists(player_file):
            self.safe_log(f"Error: {player_file} not found!")
            return

        try:
            with open(player_file, "r") as f:
                ids = [line.strip() for line in f if line.strip()]
            
            if not ids:
                self.safe_log("Error: No IDs found in file.")
                return

            self.safe_log(f"Found {len(ids)} IDs. Starting parallel batch process...")
            self.safe_log(f"Using 10 parallel tabs, 3 IDs per batch")
            self.safe_log("=" * 70)

            # Batch IDs into groups of 3
            batches = [ids[i:i + 3] for i in range(0, len(ids), 3)]
            self.safe_log(f"Total batches to process: {len(batches)}")

            # Create an asyncio queue
            queue = asyncio.Queue()
            for i, batch in enumerate(batches):
                queue.put_nowait((i + 1, batch))

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                
                self.safe_log(f"Launching 10 parallel tabs...")
                
                tasks = []
                for i in range(10):
                    task = asyncio.create_task(self.tab_worker(browser, queue, gift_code))
                    task.set_name(f"Tab-{i+1}")
                    tasks.append(task)
                
                self.safe_log("All tabs launched! Processing batches...")
                
                # Wait for all tasks to complete
                await asyncio.gather(*tasks)
                
                await browser.close()
            
            self.safe_log("=" * 70)
            self.safe_log("REDEMPTION SUMMARY")
            self.safe_log("=" * 70)
            self.safe_log(f"Total IDs Processed: {len(ids)}")
            self.safe_log(f"✓ Successful: {self.success_count}")
            self.safe_log(f"✗ Failed: {self.failed_count}")
            self.safe_log("=" * 70)
            self.safe_showinfo("Completed", f"Redemption process completed!\n\nSuccessful: {self.success_count}\nFailed: {self.failed_count}")

        except Exception as e:
            self.safe_log(f"Critical Error: {str(e)}")
            import traceback
            self.safe_log(traceback.format_exc())
            
    def run_redemption(self, gift_code):
        """Entry point for the thread to run the async loop."""
        try:
            asyncio.run(self.run_redemption_async(gift_code))
        finally:
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    app = GiftRedeemerApp(root)
    root.mainloop()
