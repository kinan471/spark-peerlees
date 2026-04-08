import sys
import subprocess
import time
import random
import json
import re
from urllib.parse import quote

# حل مشكلة pkg_resources في بيئة بايثون 3.12 على Render
try:
    import pkg_resources
except ImportError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])
        import pkg_resources
    except:
        pass

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import cloudscraper
from bs4 import BeautifulSoup

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
]

def scrape_product(url):
    html = ""
    last_error = ""
    
    # --- الطريقة الأولى: Playwright ---
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
            context = browser.new_context(user_agent=random.choice(USER_AGENTS))
            page = context.new_page()
            
            # تطبيق التمويه
            stealth = Stealth()
            stealth.apply_stealth_sync(page)

            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(random.uniform(2, 4))
            html = page.content()
            browser.close()
    except Exception as e:
        last_error = str(e)

    # --- الطريقة الثانية: Cloudscraper (Fallback) ---
    if not html or len(html) < 5000:
        try:
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url, timeout=30)
            if response.status_code == 200:
                html = response.text
        except Exception as e:
            last_error += f" | Cloudscraper failed: {str(e)}"

    if not html:
        return {'success': False, 'message': f"Failed to fetch content: {last_error}"}

    # --- استخراج البيانات ---
    soup = BeautifulSoup(html, 'lxml')
    name, price, image = "", 0.0, ""
    
    # محاولة استخراج العنوان
    title_tag = soup.select_one('h1, .product-name, .product-title')
    if title_tag: name = title_tag.get_text(strip=True)

    # محاولة استخراج السعر
    price_text = soup.find(string=re.compile(r'\d+[\.,]\d+'))
    if price_text:
        found_price = re.findall(r'\d+[\.,]\d+', price_text)
        if found_price: price = float(found_price[0].replace(',', '.'))

    return {
        'success': True,
        'name': name,
        'price': price,
        'image': image,
        'url': url
    }
