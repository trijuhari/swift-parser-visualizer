"""
Playwright scraper using Chrome user profile to access GS SWIFT docs.
"""
import asyncio
import json
import re
import os
from playwright.async_api import async_playwright

URL = "https://developer.gs.com/docs/services/transaction-banking/swift-reporting/"
# Try to use the existing Chrome profile
USER_DATA = os.path.expanduser("~/.var/app/com.google.Chrome/config/google-chrome")

async def scrape():
    async with async_playwright() as p:
        # Try with full chrome path and existing profile
        try:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir="/tmp/gs_scrape_profile",
                headless=True,
                executable_path="/app/extra/chrome",
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=WebAssemblyTrapHandler,DesktopPWAsRunOnOsLogin",
                ],
                ignore_https_errors=True,
            )
            page = browser.pages[0] if browser.pages else await browser.new_page()
        except Exception as e:
            print(f"Persistent context failed: {e}")
            # Fallback to regular launch
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            page = await browser.new_page()

        # Stealth: override navigator.webdriver
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3] });
        """)

        print(f"Navigating to {URL} ...")
        try:
            await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Navigation error: {e}")

        # Check page title
        title = await page.title()
        print(f"Page title: {title}")

        # Save full HTML
        html = await page.content()
        with open("gs_swift_raw.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Saved raw HTML: {len(html)} bytes")

        # Get all visible text
        try:
            body_text = await page.inner_text("body")
        except:
            body_text = ""

        # Try screenshot
        await page.screenshot(path="gs_swift_screenshot.png", full_page=False)
        print("Screenshot saved")

        # Look for nav links to MT sub-pages
        all_links = await page.query_selector_all("a[href]")
        mt_links = []
        for link in all_links:
            href = await link.get_attribute("href")
            txt = (await link.inner_text()).strip()
            if href and any(x in href.lower() for x in ["mt940", "mt942", "mt950"]):
                mt_links.append((txt, href))

        print(f"Found {len(mt_links)} MT-related links: {mt_links[:10]}")

        # Save for inspection
        with open("gs_swift_links.txt", "w") as f:
            for t, h in mt_links:
                f.write(f"{t}\t{h}\n")
            f.write("\n=== BODY TEXT SAMPLE ===\n")
            f.write(body_text[:5000])

        print("Saved links and body text sample to gs_swift_links.txt")
        print("\n=== BODY TEXT SAMPLE (first 2000 chars) ===")
        print(body_text[:2000])

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape())
