import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json

SITEMAP_URL = "https://www.mundoparquet.com/sitemap.xml"
OUTPUT_FILE = "products_data.json"

def fetch_sitemap(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def extract_all_urls(xml_content):
    root = ET.fromstring(xml_content)
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    return [url.find('ns:loc', ns).text for url in root.findall('ns:url', ns)]

def scrape_title(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find("title")
        return title_tag.text.strip() if title_tag else None
    except Exception as e:
        print(f"⚠️ Error scraping {url}: {e}")
        return None

def main():
    print(f"🔗 Llegint sitemap: {SITEMAP_URL}")
    xml = fetch_sitemap(SITEMAP_URL)
    urls = extract_all_urls(xml)
    
    print(f"🔎 S'han trobat {len(urls)} URLs al sitemap")
    print("📋 Primeres 10 URLs:")
    for u in urls[:10]:
        print("➡️", u)

    # Aquí pots filtrar les que siguin de productes (ajustem després si vols)
    product_urls = [u for u in urls if "/product/" in u or "/catalog/product/view" in u]
    print(f"🧪 URLs de producte filtrades: {len(product_urls)}")

    data = []
    for url in product_urls:
        title = scrape_title(url)
        if title:
            slug = url.strip('/').split('/')[-1]
            data.append({"url": url, "title": title, "slug": slug})

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ S'han guardat {len(data)} productes a {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
