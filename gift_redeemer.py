import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import asyncio
import os
from datetime import datetime
from threading import Lock

REDEEM_URL = "https://kingshot.net/gift-codes/redeem"
NUM_WINDOWS = 4

# ── Colour palette ─────────────────────────────────────────────────────────────
BG       = "#1e1e2e"
BG2      = "#181825"
BG3      = "#313244"
FG       = "#cdd6f4"
PURPLE   = "#cba6f7"
GREEN    = "#a6e3a1"
RED      = "#f38ba8"
YELLOW   = "#f9e2af"
BLUE     = "#89b4fa"
MUTED    = "#6c7086"

# One accent per browser tab
TAB_ACCENTS = ["#89b4fa", "#a6e3a1", "#f9e2af", "#cba6f7"]
TAB_LABELS  = ["Tab 1", "Tab 2", "Tab 3", "Tab 4"]


class GiftRedeemerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kingshot Gift Code Redeemer — 4-Tab Parallel")
        self.root.geometry("900x620")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self._build_ui()

        # ── Shared state ───────────────────────────────────────────────────
        self._stop_requested = False
        self._lock           = Lock()

        # Per-tab counters  [tab0, tab1, tab2, tab3]
        self.success_counts = [0, 0, 0, 0]
        self.skipped_counts = [0, 0, 0, 0]
        self.failed_counts  = [0, 0, 0, 0]
        self.failed_ids: list[str] = []

        # Track how many tabs have finished (thread-safe)
        self._tabs_done = 0

    # ──────────────────────────────────────────────────────────────────────────
    # UI Construction
    # ──────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────────────
        hdr = tk.Frame(self.root, bg=BG)
        hdr.pack(fill=tk.X, padx=16, pady=(12, 0))

        tk.Label(hdr, text="🎁 Kingshot Gift Code Redeemer",
                 font=("Arial", 14, "bold"), fg=PURPLE, bg=BG).pack(side=tk.LEFT)

        tk.Label(hdr, text="4-Window Parallel Mode",
                 font=("Arial", 9), fg=MUTED, bg=BG).pack(side=tk.LEFT, padx=(10, 0), pady=4)

        # ── Gift code + buttons ────────────────────────────────────────────
        ctrl = tk.Frame(self.root, bg=BG)
        ctrl.pack(fill=tk.X, padx=16, pady=8)

        tk.Label(ctrl, text="Gift Code:", font=("Arial", 11, "bold"),
                 fg=FG, bg=BG).pack(side=tk.LEFT, padx=(0, 6))

        self.code_entry = tk.Entry(ctrl, font=("Arial", 11), width=28,
                                   bg=BG3, fg=FG, insertbackground=FG,
                                   relief="flat", bd=4)
        self.code_entry.pack(side=tk.LEFT, padx=(0, 14))

        self.start_btn = tk.Button(ctrl, text="▶  Start Redemption",
                                   font=("Arial", 10, "bold"),
                                   bg=GREEN, fg=BG, activebackground="#94d4a0",
                                   relief="flat", padx=12, pady=5,
                                   command=self.start_process)
        self.start_btn.pack(side=tk.LEFT, padx=4)

        self.stop_btn = tk.Button(ctrl, text="⏹  Stop",
                                  font=("Arial", 10, "bold"),
                                  bg=RED, fg=BG, activebackground="#e07090",
                                  relief="flat", padx=12, pady=5,
                                  command=self.stop_process, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=4)

        # ── Overall progress bar + label ───────────────────────────────────
        prog_frame = tk.Frame(self.root, bg=BG)
        prog_frame.pack(fill=tk.X, padx=16, pady=(0, 4))

        self.progress_var = tk.StringVar(value="Ready — enter a gift code and click Start")
        tk.Label(prog_frame, textvariable=self.progress_var,
                 font=("Arial", 9), fg=BLUE, bg=BG).pack(side=tk.LEFT)

        # ── Notebook (4 tabs) ──────────────────────────────────────────────
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.TNotebook",
                        background=BG, borderwidth=0)
        style.configure("Dark.TNotebook.Tab",
                        background=BG3, foreground=FG,
                        padding=[12, 5], font=("Arial", 10, "bold"))
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", BG2)],
                  foreground=[("selected", PURPLE)])

        self.notebook = ttk.Notebook(self.root, style="Dark.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 4))

        self.log_areas: list[scrolledtext.ScrolledText] = []
        self.tab_progress_vars: list[tk.StringVar] = []

        for i in range(NUM_WINDOWS):
            tab_frame = tk.Frame(self.notebook, bg=BG2)
            self.notebook.add(tab_frame, text=f"  {TAB_LABELS[i]}  ")

            # Per-tab progress line
            pv = tk.StringVar(value="Waiting…")
            self.tab_progress_vars.append(pv)
            tk.Label(tab_frame, textvariable=pv, font=("Arial", 9),
                     fg=TAB_ACCENTS[i], bg=BG2).pack(anchor="w", padx=8, pady=(4, 0))

            log = scrolledtext.ScrolledText(tab_frame, font=("Courier", 9),
                                            bg=BG2, fg=FG,
                                            insertbackground=FG, relief="flat")
            log.pack(fill=tk.BOTH, expand=True, padx=4, pady=(2, 4))

            # Colour tags
            log.tag_config("success", foreground=GREEN)
            log.tag_config("fail",    foreground=RED)
            log.tag_config("warn",    foreground=YELLOW)
            log.tag_config("info",    foreground=TAB_ACCENTS[i])
            log.tag_config("head",    foreground=PURPLE)

            self.log_areas.append(log)

        # ── Summary bar at bottom ──────────────────────────────────────────
        self.summary_var = tk.StringVar(value="")
        tk.Label(self.root, textvariable=self.summary_var,
                 font=("Courier", 9), fg=FG, bg=BG).pack(
                     anchor="w", padx=16, pady=(0, 8))

    # ──────────────────────────────────────────────────────────────────────────
    # Thread-safe logging helpers
    # ──────────────────────────────────────────────────────────────────────────

    def tab_log(self, win_idx: int, message: str, tag: str = ""):
        """Write a timestamped line to a specific tab's log area."""
        ts   = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {message}\n"
        log  = self.log_areas[win_idx]
        log.insert(tk.END, line, tag)
        log.see(tk.END)

    def safe_tab_log(self, win_idx: int, message: str, tag: str = ""):
        self.root.after(0, lambda w=win_idx, m=message, t=tag: self.tab_log(w, m, t))

    def safe_tab_progress(self, win_idx: int, text: str):
        self.root.after(0, lambda: self.tab_progress_vars[win_idx].set(text))

    def safe_set_progress(self, text: str):
        self.root.after(0, lambda: self.progress_var.set(text))

    def safe_set_summary(self, text: str):
        self.root.after(0, lambda: self.summary_var.set(text))

    # ──────────────────────────────────────────────────────────────────────────
    # Button callbacks
    # ──────────────────────────────────────────────────────────────────────────

    def stop_process(self):
        self._stop_requested = True
        for i in range(NUM_WINDOWS):
            self.safe_tab_log(i, "⏹ Stop requested — finishing current player…", "warn")
        self.stop_btn.config(state=tk.DISABLED)

    def start_process(self):
        code = self.code_entry.get().strip()
        if not code:
            messagebox.showwarning("Input Error", "Please enter a gift code.")
            return

        # Reset state
        self._stop_requested   = False
        self._windows_done     = 0
        self.success_counts    = [0, 0, 0, 0]
        self.skipped_counts    = [0, 0, 0, 0]
        self.failed_counts     = [0, 0, 0, 0]
        self.failed_ids        = []

        # Clear all log areas
        for log in self.log_areas:
            log.delete("1.0", tk.END)
        for pv in self.tab_progress_vars:
            pv.set("Starting…")
        self.summary_var.set("")

        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)

        thread = threading.Thread(target=self.run_redemption, args=(code,), daemon=True)
        thread.start()

    # ──────────────────────────────────────────────────────────────────────────
    # Core: single-player redemption
    # ──────────────────────────────────────────────────────────────────────────

    async def redeem_for_player(self, page, player_id: str, gift_code: str,
                                win_idx: int) -> str:
        """
        Perform the full lookup + redeem flow for one player on the given page.
        Returns: 'success' | 'not_found' | 'already_redeemed' | 'invalid_code' | 'error'
        """
        def wlog(msg, tag=""):
            self.safe_tab_log(win_idx, msg, tag)

        # 1. Navigate
        try:
            await page.goto(REDEEM_URL, timeout=30000, wait_until="domcontentloaded")
        except Exception as e:
            wlog(f"  ✗ [{player_id}] Navigation error: {e}", "fail")
            return "error"

        # 2. Fill Player ID
        try:
            player_input = page.locator(
                "input[placeholder*='Player'], input[name*='player'], "
                "input[id*='player'], input[type='text']"
            ).first
            await player_input.wait_for(state="visible", timeout=15000)
            await player_input.fill(player_id)
        except Exception as e:
            wlog(f"  ✗ [{player_id}] Player ID field not found: {e}", "fail")
            return "error"

        # 3. Click Lookup Player
        try:
            lookup_btn = page.get_by_role("button", name="Lookup Player")
            await lookup_btn.click(timeout=10000)
        except Exception as e:
            wlog(f"  ✗ [{player_id}] Lookup button error: {e}", "fail")
            return "error"

        # 4. Wait for response
        try:
            await page.wait_for_selector(
                "[class*='player'], [class*='result'], [class*='error'], "
                "[class*='alert'], [class*='not-found'], [class*='invalid']",
                timeout=20000, state="visible"
            )
        except PlaywrightTimeoutError:
            wlog(f"  ? [{player_id}] No lookup response — skipping.", "warn")
            return "not_found"

        await asyncio.sleep(1)

        # 5. Check for player-not-found
        page_text = (await page.inner_text("body")).lower()
        not_found_phrases = [
            "player not found", "no player found", "invalid player",
            "player does not exist", "could not find", "player id not found"
        ]
        if any(ph in page_text for ph in not_found_phrases):
            wlog(f"  – [{player_id}] Player not found on server.", "warn")
            return "not_found"

        # 6. Fill Gift Code
        try:
            gift_input = page.locator(
                "input[placeholder*='gift'], input[id*='gift'], input[name*='gift']"
            ).first
            await gift_input.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            await gift_input.fill(gift_code)
        except Exception as e:
            wlog(f"  ✗ [{player_id}] Gift code field not found: {e}", "fail")
            return "error"

        # 7. Click Redeem Gift Code
        try:
            redeem_btn = page.get_by_role("button", name="Redeem Gift Code")
            await redeem_btn.scroll_into_view_if_needed()
            await redeem_btn.click(timeout=10000)
        except Exception as e:
            wlog(f"  ✗ [{player_id}] Redeem button error: {e}", "fail")
            return "error"

        # 8. Wait for redemption result
        try:
            await page.wait_for_selector(
                "[class*='success'], [class*='error'], [class*='alert'], "
                "[class*='toast'], [class*='notification'], [class*='message']",
                timeout=30000, state="visible"
            )
        except PlaywrightTimeoutError:
            wlog(f"  ? [{player_id}] No redemption response — treating as unknown.", "warn")
            return "error"

        await asyncio.sleep(0.8)

        # 9. Parse result
        result_text = (await page.inner_text("body")).lower()
        already_phrases = ["already redeemed", "already claimed", "code already used",
                           "duplicate", "redeemed before"]
        success_phrases = ["successfully redeemed", "redemption successful", "gift claimed",
                           "claimed successfully", "redeemed successfully", "success"]
        error_phrases   = ["invalid code", "expired", "gift code invalid",
                           "code not found", "incorrect code"]

        if any(ph in result_text for ph in already_phrases):
            wlog(f"  ~ [{player_id}] Code already redeemed (skipped).", "warn")
            return "already_redeemed"
        elif any(ph in result_text for ph in success_phrases):
            return "success"
        elif any(ph in result_text for ph in error_phrases):
            wlog(f"  ✗ [{player_id}] Invalid/expired gift code — halting window.", "fail")
            return "invalid_code"
        else:
            wlog(f"  ? [{player_id}] Ambiguous response — assuming success.", "warn")
            return "success"

    # ──────────────────────────────────────────────────────────────────────────
    # Core: one browser tab processes its chunk of IDs
    # ──────────────────────────────────────────────────────────────────────────

    async def tab_worker(self, page, tab_idx: int,
                         chunk: list[str], gift_code: str):
        """Async task for one browser tab (page). The page is created externally."""
        total_chunk = len(chunk)
        self.safe_tab_log(tab_idx,
            f"═══ {TAB_LABELS[tab_idx]} ═══  ({total_chunk} players)", "head")
        self.safe_tab_progress(tab_idx, f"Starting…")

        try:
            for idx, player_id in enumerate(chunk, start=1):
                if self._stop_requested:
                    self.safe_tab_log(tab_idx, "⏹ Stopped by user.", "warn")
                    break

                self.safe_tab_progress(tab_idx,
                    f"[{idx}/{total_chunk}]  Player: {player_id}")
                self.safe_tab_log(tab_idx,
                    f"\n[{idx}/{total_chunk}] Processing: {player_id}", "info")

                result = await self.redeem_for_player(page, player_id, gift_code, tab_idx)

                with self._lock:
                    if result == "success":
                        self.success_counts[tab_idx] += 1
                        self.safe_tab_log(tab_idx,
                            f"  ✓ [{player_id}] SUCCESSFUL.", "success")
                    elif result == "not_found":
                        self.skipped_counts[tab_idx] += 1
                        self.failed_ids.append(player_id)
                    elif result == "already_redeemed":
                        self.skipped_counts[tab_idx] += 1
                    elif result == "invalid_code":
                        self.failed_counts[tab_idx] += 1
                        self.failed_ids.append(player_id)
                        break          # gift code is globally bad — stop this tab
                    else:              # "error"
                        self.failed_counts[tab_idx] += 1
                        self.failed_ids.append(player_id)

                await asyncio.sleep(1.5)

        except Exception as e:
            self.safe_tab_log(tab_idx, f"  ✗ Unexpected error: {e}", "fail")

        # Per-tab mini summary
        s  = self.success_counts[tab_idx]
        sk = self.skipped_counts[tab_idx]
        f  = self.failed_counts[tab_idx]
        self.safe_tab_log(tab_idx, f"\n── Tab Summary ──", "head")
        self.safe_tab_log(tab_idx, f"  ✓ Success : {s}", "success")
        self.safe_tab_log(tab_idx, f"  ~ Skipped : {sk}", "warn")
        self.safe_tab_log(tab_idx, f"  ✗ Failed  : {f}", "fail")
        self.safe_tab_progress(tab_idx,
            f"Done  ✓{s}  ~{sk}  ✗{f}")

        with self._lock:
            self._tabs_done += 1

    # ──────────────────────────────────────────────────────────────────────────
    # Orchestration
    # ──────────────────────────────────────────────────────────────────────────

    async def run_redemption_async(self, gift_code: str):
        player_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "playerid.txt")

        if not os.path.exists(player_file):
            for i in range(NUM_WINDOWS):
                self.safe_tab_log(i, "✗ playerid.txt not found!", "fail")
            return

        with open(player_file, "r") as f:
            ids = [line.strip() for line in f if line.strip()]

        if not ids:
            for i in range(NUM_WINDOWS):
                self.safe_tab_log(i, "✗ No player IDs found in playerid.txt.", "fail")
            return

        total = len(ids)

        # ── Split into 4 chunks ────────────────────────────────────────────
        # First 3 windows get floor(total/4) IDs each.
        # Window 4 (index 3) gets whatever remains (handles odd totals).
        base        = total // NUM_WINDOWS
        chunks: list[list[str]] = []
        cursor = 0
        for w in range(NUM_WINDOWS - 1):
            chunks.append(ids[cursor : cursor + base])
            cursor += base
        chunks.append(ids[cursor:])   # last window gets remainder

        # Log the split plan
        self.safe_set_progress(
            f"Total: {total} players  |  Splitting across {NUM_WINDOWS} browser tabs…")
        for i, chunk in enumerate(chunks):
            self.safe_tab_log(i,
                f"Assigned {len(chunk)} players  (IDs #{(i*base)+1}–"
                f"#{(i*base)+len(chunk)})", "head")

        # ── Launch ONE browser with 4 tabs running in parallel ────────────
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=False)
            context = await browser.new_context()

            # Open 4 pages (tabs) up front inside the single browser window
            pages = [await context.new_page() for _ in range(NUM_WINDOWS)]

            tasks = [
                asyncio.create_task(
                    self.tab_worker(pages[i], i, chunks[i], gift_code),
                    name=f"Tab-{i+1}"
                )
                for i in range(NUM_WINDOWS)
            ]
            await asyncio.gather(*tasks)

            await browser.close()

        # ── Overall summary ────────────────────────────────────────────────
        total_s  = sum(self.success_counts)
        total_sk = sum(self.skipped_counts)
        total_f  = sum(self.failed_counts)

        summary_lines = [
            f"═══════════════  OVERALL SUMMARY  ═══════════════",
            f"  Total Players  : {total}",
            f"  ✓ Successful   : {total_s}",
            f"  ~ Skipped      : {total_sk}",
            f"  ✗ Failed/Error : {total_f}",
        ]
        if self.failed_ids:
            summary_lines.append(f"\n  Player IDs that failed / not found:")
            for fid in self.failed_ids:
                summary_lines.append(f"    • {fid}")
        summary_lines.append(f"══════════════════════════════════════════════════")

        for line in summary_lines:
            for i in range(NUM_WINDOWS):
                tag = ("success" if "✓" in line else
                       "warn"    if "~" in line or "•" in line else
                       "fail"    if "✗" in line else "head")
                self.safe_tab_log(i, line, tag)

        self.safe_set_progress(
            f"Done! ✓{total_s} success  ~{total_sk} skipped  ✗{total_f} failed")
        self.safe_set_summary(
            f"Overall:  ✓ {total_s} success   ~ {total_sk} skipped   ✗ {total_f} failed  "
            f"(across {NUM_WINDOWS} browser tabs)")

        self.root.after(0, lambda: messagebox.showinfo(
            "All Tabs Complete",
            f"Redemption finished across {NUM_WINDOWS} browser tabs!\n\n"
            f"✓ Successful   : {total_s}\n"
            f"~ Skipped      : {total_sk}\n"
            f"✗ Failed/Error : {total_f}\n"
            f"\nTotal Processed: {total}"
        ))

    def run_redemption(self, gift_code: str):
        """Entry point for the background thread."""
        try:
            asyncio.run(self.run_redemption_async(gift_code))
        except Exception as e:
            for i in range(NUM_WINDOWS):
                self.safe_tab_log(i, f"Critical error: {e}", "fail")
        finally:
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.config(state=tk.DISABLED))


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = GiftRedeemerApp(root)
    root.mainloop()
