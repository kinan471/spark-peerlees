import requests
import json
import re
import time
import random
from urllib.parse import quote
from django.conf import settings

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1'
]

def scrape_product(url):
    last_error = ""
    scraper_api_key = getattr(settings, 'SCRAPER_API_KEY', None)
    
    for attempt in range(3):
        try:
            if scraper_api_key:
                # Use standard proxy without rendering for speed. Metadata exists in HTML source.
                proxy_url = f"https://api.scraperapi.com?api_key={scraper_api_key}&url={quote(url)}&country_code=tr"
            else:
                proxy_url = url 

            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.google.com/'
            }
            response = requests.get(proxy_url, headers=headers, timeout=60)
            
            if response.status_code != 200:
                raise Exception(f"Request failed with status {response.status_code}")

            html = response.text
            if not html or len(html) < 500:
                raise Exception("Empty or blocked page received")

            name = ""
            price = 0.0
            image = ""
            description = ""
            specifications = {}

            # 1. JSON-LD Extraction (Primary for both Akakçe & Cimri)
            ld_scripts = re.findall(r'<script(?:\s+type="application\/ld\+json"|[^>]*)>([\s\S]*?)</script>', html, re.IGNORECASE)
            for script_content in ld_scripts:
                try:
                    data = json.loads(script_content.strip())
                    schemas = data if isinstance(data, list) else [data]
                    for schema in schemas:
                        if schema.get('@type') in ['Product', 'ProductGroup']:
                            if not name: name = schema.get('name', '')
                            if not image:
                                img = schema.get('image', '')
                                if isinstance(img, list) and img:
                                    img = img[0]
                                if isinstance(img, dict):
                                    image = img.get('url', '')
                                else:
                                    image = img
                            if not description: description = schema.get('description', '')
                            
                            if schema.get('offers'):
                                offers = schema.get('offers')
                                offer_list = offers if isinstance(offers, list) else [offers]
                                for o in offer_list:
                                    p = o.get('price') or o.get('lowPrice')
                                    if p and not price:
                                        try:
                                            price = float(str(p).replace(',', '.'))
                                        except: pass
                except: pass

            # 2. Meta Tags (Stronger Fallback)
            if not name:
                match = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', html, re.IGNORECASE)
                if match: name = match.group(1)
            if not image:
                match = re.search(r'<meta[^>]*property="og:image"[^>]*content="([^"]+)"', html, re.IGNORECASE)
                if match: image = match.group(1)
            if not description:
                match = re.search(r'<meta[^>]*property="og:description"[^>]*content="([^"]+)"', html, re.IGNORECASE)
                if match: description = match.group(1).strip()
            
            # 3. Cimri Specific Fallbacks
            if 'cimri.com' in url:
                if not price:
                    match = re.search(r'data-price="([^"]+)"', html)
                    if match: 
                        try: price = float(match.group(1))
                        except: pass
                
            # 4. Fallback Regex for Price
            if not price:
                price_blocks = re.findall(r'class="[^"]*(?:price|pt_v8|s1a|lowest-price)[^"]*"[^>]*>([\s\S]*?)</span>', html, re.IGNORECASE)
                for block in price_blocks:
                    txt = re.sub(r'<[^>]*>', '', block).strip()
                    p_str = "".join(re.findall(r'[0-9,.]', txt))
                    if p_str:
                        if ',' in p_str and '.' in p_str:
                            p_str = p_str.replace('.', '').replace(',', '.')
                        elif ',' in p_str:
                            p_str = p_str.replace(',', '.')
                        try:
                            parsed = float(p_str)
                            if parsed > 5:
                                price = parsed
                                break
                        except: pass

            # 5. Specifications
            specs_cont = re.search(r'<div[^>]*class="[^"]*(?:pt_v8|spec-list|p-detail)[^"]*"[^>]*>([\s\S]*?)</div>', html, re.IGNORECASE)
            if specs_cont:
                specs_html = specs_cont.group(1)
                li_matches = re.findall(r'<li[^>]*>\s*<span[^>]*>([\s\S]*?)</span>\s*<span[^>]*>([\s\S]*?)</span>', specs_html, re.IGNORECASE)
                for sm in li_matches:
                    key = re.sub(r'[:：]|<[^>]*>', '', sm[0]).strip()
                    val = re.sub(r'<[^>]*>', '', sm[1]).strip()
                    if key and val and len(key) < 50:
                        specifications[key] = val
                
                tr_matches = re.findall(r'<tr[^>]*>\s*<td[^>]*>([\s\S]*?)</td>\s*<td[^>]*>([\s\S]*?)</td>', specs_html, re.IGNORECASE)
                for tm in tr_matches:
                    key = re.sub(r'[:：]|<[^>]*>', '', tm[0]).strip()
                    val = re.sub(r'<[^>]*>', '', tm[1]).strip()
                    if key and val and len(key) < 50:
                        specifications[key] = val

            if not name:
                raise Exception("Could not parse product name")

            # Final Image Sanitization (Fixing 'dict' error)
            if image:
                if isinstance(image, dict):
                    image = image.get('url', '')
                
                if isinstance(image, str) and image:
                    if not image.startswith('http'):
                        image = 'https:' + (image if image.startswith('//') else '//' + image)

            return {
                'success': True,
                'name': name,
                'price': price,
                'image': image,
                'description': description,
                'specifications': specifications
            }

        except Exception as e:
            last_error = str(e)
            if attempt < 2:
                time.sleep(1)
            
    return {
        'success': False,
        'message': f"Scraping failed: {last_error}"
    }
