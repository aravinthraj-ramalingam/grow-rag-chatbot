import asyncio
import json
import logging
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

SCHEME_URLS = [
    "https://groww.in/mutual-funds/tata-large-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/tata-flexi-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/tata-elss-fund-direct-growth",
    "https://groww.in/mutual-funds/tata-multicap-fund-direct-growth"
]

async def scrape_fund_data(browser_context, url):
    logger.info(f"Scraping {url}")
    page = await browser_context.new_page()
    
    try:
        # Navigate to the URL
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # Wait for hydration
        await page.wait_for_selector("h1", timeout=30000)
        await asyncio.sleep(5)
        
        # Click "View details" for fund managers if present
        try:
            # Find all "View details" buttons in the Fund Management section
            # We use a broad selector and then filter by text or position
            view_details_buttons = await page.get_by_text("View details").all()
            for button in view_details_buttons:
                # Check if it's in the fund management area (heuristic: near "Fund management" text)
                await button.click()
                await asyncio.sleep(0.5)
        except Exception as e:
            logger.warning(f"Could not click 'View details': {e}")

        # Get content after interactions
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        fund_data = {
            "url": url,
            "fund_name": "",
            "nav": "N/A",
            "riskometer": "N/A",
            "min_investments": {},
            "returns_and_rankings": [],
            "exit_load_tax_stamp_duty": {},
            "fund_management": [],
            "faqs": []
        }
        
        # Extract Fund Name
        fund_name_tag = soup.find("h1")
        if fund_name_tag:
            fund_data["fund_name"] = fund_name_tag.text.strip()

        # 1. NAV & Riskometer
        nav_label = soup.find(string=lambda t: t and "NAV:" in t)
        if nav_label:
            nav_val = nav_label.find_next()
            if nav_val:
                fund_data["nav"] = nav_val.text.strip().replace("₹", "").strip()

        risk_text = soup.find(string=lambda t: t and "Risk" in t and "Riskometer" not in t)
        if risk_text:
            fund_data["riskometer"] = risk_text.strip()

        # 2. Minimum Investments
        min_header = soup.find(string=lambda t: t and "Minimum investments" in t)
        if min_header:
            section = min_header.find_parent("section") or min_header.find_parent("div")
            if section:
                # Use label-based search for robust extraction
                labels = ["Min. for 1st investment", "Min. for 2nd investment", "Min. for SIP", "Minimum SIP"]
                for label in labels:
                    label_el = section.find(string=lambda t: t and label.lower() in t.lower())
                    if label_el:
                        val_el = label_el.find_next()
                        if val_el:
                            fund_data["min_investments"][label] = val_el.text.strip()

        # 3. Returns & Rankings
        returns_header = soup.find(string=lambda t: t and "Returns and rankings" in t)
        if returns_header:
            table = returns_header.find_next("table")
            if table:
                headers = [th.text.strip() for th in table.find_all("th")]
                if not headers:
                    first_row = table.find("tr")
                    if first_row:
                        headers = [td.text.strip() for td in first_row.find_all("td")]
                
                if headers:
                    for row in table.find_all("tr")[1:]:
                        cells = [td.text.strip() for td in row.find_all("td")]
                        if cells and len(cells) >= len(headers):
                            fund_data["returns_and_rankings"].append(dict(zip(headers, cells[:len(headers)])))

        # 4. Exit Load, Stamp Duty and Tax
        exit_header = soup.find(string=lambda t: t and "Exit load, stamp duty and tax" in t)
        if exit_header:
            section = exit_header.find_parent("section") or exit_header.find_parent("div")
            if section:
                labels = ["Exit load", "Stamp duty", "Tax implication"]
                for label in labels:
                    label_el = section.find(string=lambda t: t and label.lower() in t.lower())
                    if label_el:
                        val_el = label_el.find_next(["p", "div"])
                        if val_el:
                            fund_data["exit_load_tax_stamp_duty"][label.lower().replace(" ", "_")] = val_el.text.strip()

        # 5. Fund Management
        mgmt_header = soup.find(string=lambda t: t and "Fund management" in t)
        if mgmt_header:
            section = mgmt_header.find_parent("section") or mgmt_header.find_parent("div")
            if section:
                # Find all manager cards/names
                cards = section.find_all("div", class_=lambda c: c and "card" in c.lower()) or section.find_all("div", style=lambda s: s and "border" in s.lower())
                if not cards:
                    # Fallback: look for "View details" buttons and their parents
                    buttons = await page.get_by_text("View details").all()
                    for btn in buttons:
                        # This is a bit complex for BS4 after clicks, let's just use robust name search
                        pass

                manager_names = section.find_all("h3")
                for name_node in manager_names:
                    name_text = name_node.text.strip()
                    if len(name_text) < 3 or name_text == "Fund management": continue
                    
                    mgr_info = {"name": name_text}
                    # Details are usually in the next sibling or a shared container
                    details_container = name_node.find_next("div", class_=lambda c: c and ("detail" in c.lower() or "bio" in c.lower() or "expand" in c.lower()))
                    if details_container:
                        mgr_info["details"] = details_container.text.strip()
                    
                    if mgr_info["name"] not in [m["name"] for m in fund_data["fund_management"]]:
                        fund_data["fund_management"].append(mgr_info)

        # 6. FAQs
        faq_questions = soup.find_all("h3")
        found_faqs = []
        for q in faq_questions:
            q_text = q.text.strip()
            # FAQs are distinct from Manager names which are also in h3
            if (q_text.endswith("?") or any(w in q_text.lower() for w in ["how", "what", "is", "when", "can"])) and len(q_text) > 20:
                answer_el = q.find_next(["div", "p", "section"])
                if answer_el:
                    found_faqs.append({
                        "question": q_text,
                        "answer": answer_el.text.strip()
                    })
        fund_data["faqs"] = found_faqs

        return fund_data

    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return {"url": url, "error": str(e)}
    finally:
        await page.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        results = []
        for url in SCHEME_URLS:
            data = await scrape_fund_data(context, url)
            results.append(data)
            await asyncio.sleep(2)
            
        with open("fund_data.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
            
        logger.info("Scraping completed. Data saved to fund_data.json")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
