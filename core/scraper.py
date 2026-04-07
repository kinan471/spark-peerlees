from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import cloudscraper
import json
import re
import time
import random
from urllib.parse import quote
from django.conf import settings
from bs4 import BeautifulSoup

# --- إعدادات التمويه ---
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
]

# قائمة البروكسيات - أضف البروكسيات الخاصة بك هنا
# التنسيق: 'http://username:password@ip:port' أو 'http://ip:port'
PROXY_LIST = [
    # 'http://your_proxy_1',
    # 'http://your_proxy_2',
]

def scrape_product(url):
    """
    النسخة النهائية والمطورة:
    1. تستخدم Playwright مع Stealth لتجاوز كشف البوتات.
    2. تستخدم Proxy متغير لتجنب حظر الـ IP.
    3. تستخدم Cloudscraper كخطة بديلة (Fallback).
    """
    html = ""
    last_error = ""
    
    # اختيار بروكسي عشوائي إذا كانت القائمة غير فارغة
    selected_proxy = random.choice(PROXY_LIST) if PROXY_LIST else None

    # --- الطريقة الأولى: Playwright مع التخفي والبروكسي ---
    try:
        with sync_playwright() as p:
            # إعدادات التشغيل لتجاوز الحماية
            launch_args = [
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
            
            launch_options = {
                "headless": True,
                "args": launch_args
            }
            
            if selected_proxy:
                launch_options["proxy"] = {"server": selected_proxy}

            browser = p.chromium.launch(**launch_options)
            
            # إنشاء سياق متصفح واقعي
            context = browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={'width': 1920, 'height': 1080},
                extra_http_headers={"Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"}
            )
            
            page = context.new_page()
            
            # تفعيل التخفي (Stealth)
            stealth = Stealth()
            stealth.apply_stealth_sync(page)

            # محاولة الدخول للموقع
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # محاكاة حركة بشرية (تأخير عشوائي وتمرير)
            time.sleep(random.uniform(2, 4))
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3)")
            
            # الانتظار حتى يظهر العنوان (دليل على نجاح التحميل)
            try:
                page.wait_for_selector('h1, .product-name', timeout=10000)
            except:
                pass 

            html = page.content()
            browser.close()
            
    except Exception as e:
        last_error = f"Playwright/Proxy failed: {str(e)}"

    # --- الطريقة الثانية: Cloudscraper (إذا فشل المتصفح أو كان المحتوى ناقصاً) ---
    if not html or len(html) < 5000: # التحقق من طول المحتوى لضمان عدم تحميل صفحة خطأ
        try:
            scraper = cloudscraper.create_scraper(
                browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
            )
            # استخدام البروكسي أيضاً مع cloudscraper إذا توفر
            proxies = {"http": selected_proxy, "https": selected_proxy} if selected_proxy else None
            response = scraper.get(url, timeout=30, proxies=proxies)
            
            if response.status_code == 200:
                html = response.text
        except Exception as e:
            last_error += f" | Cloudscraper failed: {str(e)}"

    if not html:
        return {'success': False, 'message': f"Scraping Blocked: {last_error}"}

    # --- مرحلة استخراج البيانات (BeautifulSoup) ---
    soup = BeautifulSoup(html, 'lxml')
    name, price, image, description = "", 0.0, "", ""
    specifications = {}

    # 1. استخراج بيانات JSON-LD (الطريقة الأدق)
    ld_json = soup.find_all('script', type='application/ld+json')
    for script in ld_json:
        try:
            if not script.string: continue
            data = json.loads(script.string)
            items = data if isinstance(data, list) else [data]
            for item in items:
                if '@graph' in item: items.extend(item['@graph'])
                
                if item.get('@type') in ['Product', 'ProductGroup']:
                    name = name or item.get('name', '')
                    img = item.get('image', '')
                    if isinstance(img, list) and img: image = image or img[0]
                    elif isinstance(img, str): image = image or img
                    
                    description = description or item.get('description', '')
                    
                    offers = item.get('offers')
                    if offers:
                        offer_list = offers if isinstance(offers, list) else [offers]
                        for o in offer_list:
                            p = o.get('price') or o.get('lowPrice')
                            if p and not price:
                                try:
                                    p_str = str(p).replace(' ', '').replace('TL', '').replace('TRY', '')
                                    p_str = p_str.replace('.', '').replace(',', '.') if ',' in p_str and '.' in p_str else p_str.replace(',', '.')
                                    price = float(p_str)
                                except: pass
        except: continue

    # 2. البحث عن العنوان والسعر عبر CSS Selectors (إذا فشل JSON-LD)
    if not name:
        h1 = soup.select_one('.p-v8 h1, h1#p-title, .pt_v8 h1, h1.product-name, .product-title')
        if h1: name = h1.get_text(strip=True)

    if not price or price == 0.0:
        price_selectors = ['.pt_v8 .pb_v8', '.p_v8 b', '.lowest-price', '.current-price', '#price-value']
        for sel in price_selectors:
            p_tag = soup.select_one(sel)
            if p_tag:
                p_text = "".join(re.findall(r'[0-9,.]', p_tag.get_text()))
                try:
                    if ',' in p_text and '.' in p_text: p_text = p_text.replace('.', '').replace(',', '.')
                    elif ',' in p_text: p_text = p_text.replace(',', '.')
                    price = float(p_text)
                    if price > 0: break
                except: pass

    # 3. استخراج المواصفات الفنية
    for row in soup.select('tr, li'):
        cols = row.select('td, th, span, div')
        if len(cols) >= 2:
            k = cols[0].get_text(strip=True).replace(':', '')
            v = cols[1].get_text(strip=True)
            if k and v and len(k) < 50:
                specifications[k] = v

    # تنظيف رابط الصورة
    if image and isinstance(image, str) and not image.startswith('http'):
        image = 'https:' + (image if image.startswith('//') else '//' + image)

    if not name:
        return {'success': False, 'message': "Blocked: Could not parse product details."}

    return {
        'success': True,
        'name': name,
        'price': price,
        'image': image,
        'description': description or name,
        'specifications': specifications
    }
