import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import asyncio
import os
import time
from datetime import datetime

REDEEM_URL = "https://kingshot.net/gift-codes/redeem"


class GiftRedeemerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kingshot Gift Code Redeemer - One-by-One")
        self.root.geometry("750x560")
        self.root.configure(bg="#1e1e2e")

        # ── Title ──────────────────────────────────────────────────────────
        title = tk.Label(root, text="🎁 Kingshot Gift Code Redeemer",
                         font=("Arial", 14, "bold"), fg="#cba6f7", bg="#1e1e2e")
        title.pack(pady=(14, 2))

        subtitle = tk.Label(root, text="One-by-one redemption via kingshot.net/gift-codes/redeem",
                            font=("Arial", 9), fg="#6c7086", bg="#1e1e2e")
        subtitle.pack()

        # ── Gift Code Input ────────────────────────────────────────────────
        frame = tk.Frame(root, bg="#1e1e2e")
        frame.pack(pady=10)

        tk.Label(frame, text="Gift Code:", font=("Arial", 11, "bold"),
                 fg="#cdd6f4", bg="#1e1e2e").grid(row=0, column=0, padx=8, sticky="w")

        self.code_entry = tk.Entry(frame, font=("Arial", 11), width=32,
                                   bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4",
                                   relief="flat", bd=4)
        self.code_entry.grid(row=0, column=1, padx=8)

        # ── Controls ───────────────────────────────────────────────────────
        ctrl_frame = tk.Frame(root, bg="#1e1e2e")
        ctrl_frame.pack(pady=6)

        self.start_button = tk.Button(ctrl_frame, text="▶  Start Redemption",
                                      font=("Arial", 11, "bold"),
                                      bg="#a6e3a1", fg="#1e1e2e", activebackground="#94d4a0",
                                      relief="flat", padx=16, pady=6,
                                      command=self.start_process)
        self.start_button.grid(row=0, column=0, padx=8)

        self.stop_button = tk.Button(ctrl_frame, text="⏹  Stop",
                                     font=("Arial", 11, "bold"),
                                     bg="#f38ba8", fg="#1e1e2e", activebackground="#e07090",
                                     relief="flat", padx=16, pady=6,
                                     command=self.stop_process, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=8)

        # ── Progress label ─────────────────────────────────────────────────
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = tk.Label(root, textvariable=self.progress_var,
                                       font=("Arial", 10), fg="#89b4fa", bg="#1e1e2e")
        self.progress_label.pack()

        # ── Log Area ───────────────────────────────────────────────────────
        log_frame = tk.Frame(root, bg="#1e1e2e")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(4, 14))

        self.log_area = scrolledtext.ScrolledText(log_frame, width=90, height=20,
                                                  font=("Courier", 9),
                                                  bg="#181825", fg="#cdd6f4",
                                                  insertbackground="#cdd6f4",
                                                  relief="flat")
        self.log_area.pack(fill=tk.BOTH, expand=True)

        # colour tags
        self.log_area.tag_config("success", foreground="#a6e3a1")
        self.log_area.tag_config("fail",    foreground="#f38ba8")
        self.log_area.tag_config("warn",    foreground="#f9e2af")
        self.log_area.tag_config("info",    foreground="#89b4fa")
        self.log_area.tag_config("head",    foreground="#cba6f7")

        # ── State ──────────────────────────────────────────────────────────
        self._stop_requested = False
        self.success_count = 0
        self.failed_count  = 0
        self.skipped_count = 0
        self.failed_ids: list[str] = []

    # ── Logging helpers ────────────────────────────────────────────────────

    def log(self, message: str, tag: str = ""):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {message}\n"
        self.log_area.insert(tk.END, line, tag)
        self.log_area.see(tk.END)

    def safe_log(self, message: str, tag: str = ""):
        self.root.after(0, lambda m=message, t=tag: self.log(m, t))

    def safe_set_progress(self, text: str):
        self.root.after(0, lambda: self.progress_var.set(text))

    # ── Button callbacks ───────────────────────────────────────────────────

    def stop_process(self):
        self._stop_requested = True
        self.safe_log("⏹ Stop requested — will halt after current player.", "warn")
        self.stop_button.config(state=tk.DISABLED)

    def start_process(self):
        code = self.code_entry.get().strip()
        if not code:
            messagebox.showwarning("Input Error", "Please enter a gift code.")
            return

        self._stop_requested = False
        self.success_count = 0
        self.failed_count  = 0
        self.skipped_count = 0
        self.failed_ids    = []

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        thread = threading.Thread(target=self.run_redemption, args=(code,), daemon=True)
        thread.start()

    # ── Core async logic ───────────────────────────────────────────────────

    async def redeem_for_player(self, page, player_id: str, gift_code: str) -> str:
        """
        Returns one of: 'success', 'not_found', 'already_redeemed', 'error'
        """
        try:
            # 1. Navigate to the redemption page
            await page.goto(REDEEM_URL, timeout=30000, wait_until="domcontentloaded")
        except Exception as e:
            self.safe_log(f"  ✗ [{player_id}] Navigation error: {e}", "fail")
            return "error"

        try:
            # 2. Fill Player ID
            player_input = page.locator("input[placeholder*='Player'], input[name*='player'], input[id*='player'], input[type='text']").first
            await player_input.wait_for(state="visible", timeout=15000)
            await player_input.fill(player_id)
        except Exception as e:
            self.safe_log(f"  ✗ [{player_id}] Could not find Player ID field: {e}", "fail")
            return "error"

        try:
            # 3. Click "Lookup Player"
            lookup_btn = page.get_by_role("button", name="Lookup Player")
            await lookup_btn.click(timeout=10000)
        except Exception as e:
            self.safe_log(f"  ✗ [{player_id}] Lookup button not found: {e}", "fail")
            return "error"

        # 4. Wait for either a player card or an error message
        try:
            await page.wait_for_selector(
                # Player card appears OR an error element appears
                "[class*='player'], [class*='result'], [class*='error'], "
                "[class*='alert'], [class*='not-found'], [class*='invalid']",
                timeout=20000,
                state="visible"
            )
        except PlaywrightTimeoutError:
            self.safe_log(f"  ? [{player_id}] No response after lookup — skipping.", "warn")
            return "not_found"

        # Short pause for the DOM to settle
        await asyncio.sleep(1)

        # 5. Detect player-not-found state by checking visible error text
        page_text = (await page.inner_text("body")).lower()
        not_found_phrases = [
            "player not found", "no player found", "invalid player",
            "player does not exist", "could not find", "player id not found"
        ]
        if any(p in page_text for p in not_found_phrases):
            self.safe_log(f"  – [{player_id}] Player not found on server.", "warn")
            return "not_found"

        # 6. Scroll to the Gift Code section
        try:
            gift_section = page.locator("input[placeholder*='gift'], input[id*='gift'], input[name*='gift']").first
            await gift_section.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            await gift_section.fill(gift_code)
        except Exception as e:
            self.safe_log(f"  ✗ [{player_id}] Gift code field not found: {e}", "fail")
            return "error"

        try:
            # 7. Click "Redeem Gift Code"
            redeem_btn = page.get_by_role("button", name="Redeem Gift Code")
            await redeem_btn.scroll_into_view_if_needed()
            await redeem_btn.click(timeout=10000)
        except Exception as e:
            self.safe_log(f"  ✗ [{player_id}] Redeem button not found: {e}", "fail")
            return "error"

        # 8. Wait for result feedback
        try:
            await page.wait_for_selector(
                "[class*='success'], [class*='error'], [class*='alert'], "
                "[class*='toast'], [class*='notification'], [class*='message']",
                timeout=30000,
                state="visible"
            )
        except PlaywrightTimeoutError:
            self.safe_log(f"  ? [{player_id}] No redemption response — treating as unknown.", "warn")
            return "error"

        await asyncio.sleep(0.8)

        # 9. Parse the result
        result_text = (await page.inner_text("body")).lower()

        already_phrases = ["already redeemed", "already claimed", "code already used",
                           "duplicate", "redeemed before"]
        success_phrases = ["successfully redeemed", "redemption successful", "gift claimed",
                           "claimed successfully", "redeemed successfully", "success"]
        error_phrases   = ["invalid code", "expired", "gift code invalid",
                           "code not found", "incorrect code"]

        if any(p in result_text for p in already_phrases):
            self.safe_log(f"  ~ [{player_id}] Code already redeemed (skipped).", "warn")
            return "already_redeemed"
        elif any(p in result_text for p in success_phrases):
            return "success"
        elif any(p in result_text for p in error_phrases):
            self.safe_log(f"  ✗ [{player_id}] Invalid/expired gift code — halting.", "fail")
            return "invalid_code"
        else:
            # Fallback: assume success if no explicit failure found
            self.safe_log(f"  ? [{player_id}] Ambiguous response — assuming success.", "warn")
            return "success"

    async def run_redemption_async(self, gift_code: str):
        player_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "playerid.txt")

        if not os.path.exists(player_file):
            self.safe_log(f"✗ playerid.txt not found at: {player_file}", "fail")
            return

        with open(player_file, "r") as f:
            ids = [line.strip() for line in f if line.strip()]

        if not ids:
            self.safe_log("✗ No player IDs found in playerid.txt.", "fail")
            return

        total = len(ids)
        self.safe_log(f"═══════════════════════════════════════════════", "head")
        self.safe_log(f"  Kingshot Gift Code Redeemer — One-by-One", "head")
        self.safe_log(f"  Gift Code : {gift_code}", "head")
        self.safe_log(f"  Players   : {total}", "head")
        self.safe_log(f"═══════════════════════════════════════════════", "head")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page    = await context.new_page()

            for idx, player_id in enumerate(ids, start=1):
                if self._stop_requested:
                    self.safe_log("⏹ Stopped by user.", "warn")
                    break

                self.safe_set_progress(f"Processing {idx}/{total} — Player {player_id}")
                self.safe_log(f"\n[{idx}/{total}] Processing player: {player_id}", "info")

                result = await self.redeem_for_player(page, player_id, gift_code)

                if result == "success":
                    self.success_count += 1
                    self.safe_log(f"  ✓ [{player_id}] Redemption SUCCESSFUL.", "success")
                elif result == "not_found":
                    self.skipped_count += 1
                    self.failed_ids.append(player_id)
                elif result == "already_redeemed":
                    self.skipped_count += 1
                elif result == "invalid_code":
                    # The gift code itself is bad — no point continuing
                    self.failed_ids.append(player_id)
                    self.failed_count += 1
                    break
                else:  # "error"
                    self.failed_count += 1
                    self.failed_ids.append(player_id)

                # Small polite delay between requests
                await asyncio.sleep(1.5)

            await browser.close()

        # ── Summary ─────────────────────────────────────────────────────
        self.safe_log(f"\n═══════════════════════════════════════════════", "head")
        self.safe_log(f"  REDEMPTION SUMMARY", "head")
        self.safe_log(f"═══════════════════════════════════════════════", "head")
        self.safe_log(f"  Total Players  : {total}", "info")
        self.safe_log(f"  ✓ Successful   : {self.success_count}", "success")
        self.safe_log(f"  ~ Skipped      : {self.skipped_count}", "warn")
        self.safe_log(f"  ✗ Failed/Error : {self.failed_count}", "fail")

        if self.failed_ids:
            self.safe_log(f"\n  Player IDs that failed / not found:", "warn")
            for fid in self.failed_ids:
                self.safe_log(f"    • {fid}", "warn")

        self.safe_log(f"═══════════════════════════════════════════════", "head")

        self.root.after(0, lambda: messagebox.showinfo(
            "Redemption Complete",
            f"Done!\n\n"
            f"✓ Successful   : {self.success_count}\n"
            f"~ Skipped      : {self.skipped_count}\n"
            f"✗ Failed/Error : {self.failed_count}"
        ))

    def run_redemption(self, gift_code: str):
        """Entry point for the background thread."""
        try:
            asyncio.run(self.run_redemption_async(gift_code))
        except Exception as e:
            self.safe_log(f"Critical error: {e}", "fail")
        finally:
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_button.config(state=tk.DISABLED))
            self.safe_set_progress("Ready")


if __name__ == "__main__":
    root = tk.Tk()
    app = GiftRedeemerApp(root)
    root.mainloop()
