import sys
import subprocess
import time
import random
import json
import re
from urllib.parse import quote

def ensure_dependencies():
    """تأكد من وجود setuptools لتوفير pkg_resources قبل استيراد المكتبات الحساسة"""
    try:
        import pkg_resources
    except ImportError:
        try:
            # محاولة تثبيت setuptools في وقت التشغيل إذا لم تكن موجودة
            subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])
            import pkg_resources
        except Exception as e:
            print(f"Critical Warning: Could not install setuptools: {e}")

def scrape_product(url):
    """
    النسخة الاحترافية:
    تتجنب ModuleNotFoundError عبر تأخير الاستيراد (Lazy Import)
    تستخدم Playwright كخيار أول و Cloudscraper كبديل.
    """
    
    # 1. التأكد من المكتبات المساعدة أولاً
    ensure_dependencies()

    # 2. استيراد المكتبات الثقيلة هنا لمنع خطأ البناء (Build Error)
    try:
        from playwright.sync_api import sync_playwright
        from playwright_stealth import Stealth
        import cloudscraper
        from bs4 import BeautifulSoup
    except ImportError as e:
        return {'success': False, 'message': f"Missing Library after Lazy Import: {str(e)}"}

    html = ""
    last_error = ""
    
    # قائمة بمتصفحات وهمية للتمويه
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    ]

    # --- الطريقة الأولى: Playwright (المحرك الأساسي) ---
    try:
        with sync_playwright() as p:
            # تشغيل المتصفح في وضع الخفاء وبدون Sandbox ليتوافق مع Render
            browser = p.chromium.launch(
                headless=True, 
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-blink-features=AutomationControlled']
            )
            
            context = browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            # تطبيق تقنية Stealth لتجاوز كشف البوتات
            stealth = Stealth()
            stealth.apply_stealth_sync(page)

            # التوجه للرابط مع انتظار تحميل العناصر الأساسية
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # محاكاة سلوك بشري بسيط
            time.sleep(random.uniform(2, 5))
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 4)")
            
            html = page.content()
            browser.close()
            
    except Exception as e:
        last_error = f"Playwright Error: {str(e)}"

    # --- الطريقة الثانية: Cloudscraper (خطة بديلة إذا فشل المتصفح) ---
    if not html or len(html) < 5000:
        try:
            scraper = cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
            )
            response = scraper.get(url, timeout=30)
            if response.status_code == 200:
                html = response.text
        except Exception as e:
            last_error += f" | Cloudscraper Error: {str(e)}"

    if not html:
        return {'success': False, 'message': f"Scraping Blocked or Failed: {last_error}"}

    # --- معالجة البيانات باستخدام BeautifulSoup ---
    soup = BeautifulSoup(html, 'lxml')
    name, price, image, description = "", 0.0, "", ""
    specifications = {}

    # 1. استخراج البيانات من JSON-LD (الخيار الأدق)
    scripts = soup.find_all('script', type='application/ld+json')
    for script in scripts:
        try:
            if not script.string: continue
            data = json.loads(script.string)
            if isinstance(data, list): data = data[0]
            if data.get('@type') == 'Product' or 'name' in data:
                name = data.get('name', name)
                image = data.get('image', image)
                description = data.get('description', description)
                offers = data.get('offers', {})
                if isinstance(offers, dict):
                    price = offers.get('price', price)
                elif isinstance(offers, list):
                    price = offers[0].get('price', price)
        except: continue

    # 2. استخراج البيانات يدوياً عبر الكلاسات إذا فشل JSON-LD
    if not name:
        title_tag = soup.select_one('h1, .product-name, .product-title, #product-name')
        if title_tag: name = title_tag.get_text(strip=True)

    if not price or price == 0:
        # البحث عن أنماط الأسعار (مثال: 1.250,00 TL)
        price_tags = soup.select('.price, .current-price, .product-price, [itemprop="price"]')
        for tag in price_tags:
            text = tag.get_text()
            clean_price = "".join(re.findall(r'[0-9,.]', text))
            try:
                if ',' in clean_price and '.' in clean_price:
                    clean_price = clean_price.replace('.', '').replace(',', '.')
                elif ',' in clean_price:
                    clean_price = clean_price.replace(',', '.')
                price = float(clean_price)
                if price > 0: break
            except: continue

    # تنظيف الروابط
    if isinstance(image, list) and image: image = image[0]
    if image and image.startswith('//'): image = 'https:' + image

    if not name:
        return {'success': False, 'message': "Could not parse product name (Possible block)"}

    return {
        'success': True,
        'name': name,
        'price': float(price) if price else 0.0,
        'image': image,
        'description': description or name,
        'specifications': specifications,
        'url': url
    }
