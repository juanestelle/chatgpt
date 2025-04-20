import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json

SITEMAP_URL = "https://www.mundoparquet.com/sitemap.xml"
OUTPUT_FILE = "products_data.json"

def fetch_sitemap(url):
    print(f"🔗 Llegint sitemap: {url}")
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def extract_subsitemaps(xml_content):
    root = ET.fromstring(xml_content)
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    return [url.find('ns:loc', ns).text for url in root.findall('ns:url', ns) if url.find('ns:loc', ns).text.endswith('.xml')]

def extract_product_urls_from_sitemap(url):
    try:
        xml = fetch_sitemap(url)
        root = ET.fromstring(xml)
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [u.find('ns:loc', ns).text for u in root.findall('ns:url', ns)]
        product_urls = [u for u in urls if "/product/" in u or "/catalog/product/" in u]
        return product_urls
    except Exception as e:
        print(f"⚠️ Error carregant sub-sitemap {url}: {e}")
        return []

def scrape_title(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find("title").text.strip()
        return title
    except Exception as e:
        print(f"⚠️ Error a {url}: {e}")
        return None

def main():
    sitemap = fetch_sitemap(SITEMAP_URL)
    subsitemaps = extract_subsitemaps(sitemap)
    
    all_product_urls = []
    for sub in subsitemaps:
        all_product_urls.extend(extract_product_urls_from_sitemap(sub))

    print(f"🔎 S'han trobat {len(all_product_urls)} productes")
    
    data = []
    for url in all_product_urls:
        title = scrape_title(url)
        if title:
            slug = url.strip('/').split('/')[-1]
            data.append({"url": url, "title": title, "slug": slug})
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ S'han guardat {len(data)} productes a {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
