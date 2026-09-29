"""CITS3006 WEB-02 reviewer bot.
Polls the app for reported payloads and visits /search?q=<payload> in a real
headless browser while holding the privileged reviewer cookie, so a reflected
XSS payload executes with access to /review.
"""
import os, time, requests
from playwright.sync_api import sync_playwright

BASE = os.environ.get("TARGET", "http://web02:5000")
REVIEWER_COOKIE = os.environ.get("REVIEWER_COOKIE", "r3v13w-s3ss-2026")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "bot-internal-1f4c")

def visit(pw, q):
    browser = pw.chromium.launch(args=["--no-sandbox"])
    ctx = browser.new_context()
    ctx.add_cookies([{"name": "reviewer", "value": REVIEWER_COOKIE,
                      "url": BASE}])
    page = ctx.new_page()
    page.goto(f"{BASE}/search?q={q}", wait_until="networkidle", timeout=10000)
    page.wait_for_timeout(1500)   # let injected script fire its fetches
    browser.close()

def main():
    with sync_playwright() as pw:
        while True:
            try:
                items = requests.get(f"{BASE}/queue",
                                     params={"token": BOT_TOKEN}, timeout=5).json()
            except Exception:
                items = []
            for q in items:
                try: visit(pw, q)
                except Exception as e: print("visit error:", e, flush=True)
            time.sleep(3)

if __name__ == "__main__":
    main()
