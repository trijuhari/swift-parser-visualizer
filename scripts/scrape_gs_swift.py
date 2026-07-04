"""
Playwright scraper for Goldman Sachs SWIFT Reporting documentation.
Extracts MT940, MT942, MT950 field tables and outputs structured JSON.
"""
import asyncio
import json
import re
from playwright.async_api import async_playwright

URL = "https://developer.gs.com/docs/services/transaction-banking/swift-reporting/"

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print(f"Navigating to {URL} ...")
        await page.goto(URL, wait_until="networkidle", timeout=60000)

        # Wait a bit more for JS to render fully
        await asyncio.sleep(3)

        # Save page HTML for inspection
        html = await page.content()
        with open("gs_swift_raw.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Saved raw HTML ({len(html)} bytes)")

        # Try to find all tabs / nav items for MT940, MT942, MT950
        tabs = await page.query_selector_all("a, button, [role='tab']")
        tab_texts = []
        for t in tabs:
            txt = (await t.inner_text()).strip()
            if any(mt in txt.upper() for mt in ["MT940", "MT942", "MT950", "MT 940", "MT 942", "MT 950"]):
                tab_texts.append(txt)
        print("Found MT tabs:", tab_texts)

        all_data = []

        # Check if there are separate tabs for each MT type
        mt_tabs = await page.query_selector_all("a[href*='mt940'], a[href*='mt942'], a[href*='mt950'], "
                                                  "button:has-text('MT940'), button:has-text('MT942'), button:has-text('MT950'), "
                                                  "button:has-text('MT 940'), button:has-text('MT 942'), button:has-text('MT 950'), "
                                                  "[role='tab']:has-text('MT940'), [role='tab']:has-text('MT942'), [role='tab']:has-text('MT950'), "
                                                  "[role='tab']:has-text('MT 940'), [role='tab']:has-text('MT 942'), [role='tab']:has-text('MT 950')")

        if mt_tabs:
            print(f"Found {len(mt_tabs)} MT-specific tabs")
            for tab in mt_tabs:
                txt = (await tab.inner_text()).strip()
                print(f"  Clicking tab: {txt}")
                await tab.click()
                await asyncio.sleep(2)
                data = await extract_tables(page, txt)
                all_data.extend(data)
        else:
            print("No separate tabs found, extracting all tables from page")
            # Try navigating to sub-pages
            sub_urls = [
                ("mt940", URL + "mt940/"),
                ("mt942", URL + "mt942/"),
                ("mt950", URL + "mt950/"),
            ]
            for msg_type, sub_url in sub_urls:
                print(f"  Trying sub-URL: {sub_url}")
                try:
                    await page.goto(sub_url, wait_until="networkidle", timeout=30000)
                    await asyncio.sleep(2)
                    data = await extract_tables(page, msg_type)
                    if data:
                        all_data.extend(data)
                        print(f"    Found {len(data)} rows for {msg_type}")
                    else:
                        print(f"    No data found at {sub_url}")
                except Exception as e:
                    print(f"    Error: {e}")

            # Go back to main page and extract everything
            await page.goto(URL, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(3)
            data = await extract_tables(page, "all")
            if data:
                print(f"  Found {len(data)} rows from main page")
                all_data.extend(data)

        await browser.close()

        # Deduplicate
        seen = set()
        unique = []
        for row in all_data:
            key = (row["msg"], row["tag"], row["sub"], row["name"])
            if key not in seen:
                seen.add(key)
                unique.append(row)

        print(f"\nTotal unique rows extracted: {len(unique)}")
        with open("gs_swift_data.json", "w", encoding="utf-8") as f:
            json.dump(unique, f, indent=2, ensure_ascii=False)
        print("Saved to gs_swift_data.json")
        return unique


async def extract_tables(page, context_hint=""):
    """Extract all tables from current page and try to parse MT tag data."""
    data = []

    # Get all table elements
    tables = await page.query_selector_all("table")
    print(f"  Found {len(tables)} tables on page (context: {context_hint})")

    for table_idx, table in enumerate(tables):
        # Get headers
        headers = []
        th_els = await table.query_selector_all("thead th, thead td, tr:first-child th, tr:first-child td")
        for th in th_els:
            headers.append((await th.inner_text()).strip().lower())

        rows = await table.query_selector_all("tbody tr, tr:not(:first-child)")
        print(f"    Table {table_idx}: headers={headers}, rows={len(rows)}")

        for row in rows:
            cells = await row.query_selector_all("td, th")
            if len(cells) < 2:
                continue
            cell_texts = [(await c.inner_text()).strip() for c in cells]

            parsed = parse_row(cell_texts, headers, context_hint)
            if parsed:
                data.append(parsed)

    # Also try to find data in definition lists or structured divs
    # Look for patterns like "Field Tag:", "Tag:", etc.
    body_text = await page.inner_text("body")
    dl_data = parse_body_text(body_text, context_hint)
    if dl_data:
        print(f"  Extracted {len(dl_data)} rows from body text parsing")
        data.extend(dl_data)

    return data


def parse_row(cells, headers, context_hint):
    """Try to map cells to our expected schema."""
    if not cells or len(cells) < 2:
        return None

    row = {
        "msg": normalize_msg(context_hint),
        "tag": "",
        "sub": "",
        "name": "",
        "len": "",
        "mo": "m",
        "sample": "",
        "desc": ""
    }

    # Try to match by header names
    col_map = {}
    for i, h in enumerate(headers):
        if any(x in h for x in ["tag", "field tag", "swift tag"]):
            col_map["tag"] = i
        elif any(x in h for x in ["sub", "subfield"]):
            col_map["sub"] = i
        elif any(x in h for x in ["name", "field name", "description", "field"]):
            col_map["name"] = i
        elif any(x in h for x in ["m/o", "mandatory", "optional", "status"]):
            col_map["mo"] = i
        elif any(x in h for x in ["format", "length", "len"]):
            col_map["len"] = i
        elif any(x in h for x in ["sample", "example", "value"]):
            col_map["sample"] = i
        elif any(x in h for x in ["desc", "notes", "remark", "comment"]):
            col_map["desc"] = i
        elif any(x in h for x in ["message", "msg", "type"]):
            col_map["msg_col"] = i

    # Assign values from mapped columns
    for field, idx in col_map.items():
        if idx < len(cells):
            val = cells[idx].strip()
            if field == "mo":
                val = "m" if any(x in val.lower() for x in ["m", "mandatory", "required"]) else "o"
            if field == "msg_col":
                row["msg"] = normalize_msg(val)
            else:
                row[field] = val

    # If no column mapping worked, try positional assignment
    if not col_map and len(cells) >= 3:
        row["tag"] = cells[0]
        row["name"] = cells[1] if len(cells) > 1 else ""
        row["mo"] = "m" if len(cells) > 2 and "m" in cells[2].lower() else "o"
        if len(cells) > 3:
            row["desc"] = cells[-1]

    # Skip rows that are empty or header-like
    if not row["tag"] and not row["name"]:
        return None
    if row["tag"].lower() in ["tag", "field", "swift tag", ""]:
        return None

    return row


def normalize_msg(hint):
    hint = str(hint).upper().replace(" ", "")
    if "940" in hint:
        return "mt940"
    elif "942" in hint:
        return "mt942"
    elif "950" in hint:
        return "mt950"
    return "mt940"  # default


def parse_body_text(text, context_hint):
    """Try to find structured data in plain text body."""
    data = []
    # Look for patterns like ":20:" or "Tag 20" or "Field 20"
    # These are SWIFT tag references
    patterns = [
        r':(\d+[A-Z]?):\s+(.+?)(?=:\d+[A-Z]?:|$)',
        r'Tag\s+(\d+[A-Z]?)\s*[-–]\s*(.+?)(?=Tag\s+\d+|$)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
        for tag, desc in matches:
            tag = tag.strip()
            desc = desc.strip()[:200]
            if tag and desc and len(desc) > 5:
                data.append({
                    "msg": normalize_msg(context_hint),
                    "tag": tag,
                    "sub": "",
                    "name": desc[:60],
                    "len": "",
                    "mo": "m",
                    "sample": "",
                    "desc": desc
                })
    return data


if __name__ == "__main__":
    asyncio.run(scrape())
