import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json

MAIN_SITEMAP_URL = "https://www.mundoparquet.com/sitemap.xml"
OUTPUT_FILE = "products_data.json"

def fetch_xml(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def get_sub_sitemaps(xml_content):
    root = ET.fromstring(xml_content)
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    return [loc.text for loc in root.findall('ns:url/ns:loc', ns) if 'sitemap' in loc.text]

def extract_product_urls_from_sitemap(xml_content):
    root = ET.fromstring(xml_content)
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    return [
        url.find('ns:loc', ns).text
        for url in root.findall('ns:url', ns)
        if "/catalog/product/view" in url.find('ns:loc', ns).text
    ]

def scrape_title(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find("title")
        return title.text.strip() if title else None
    except Exception as e:
        print(f"❌ Error amb {url}: {e}")
        return None

def main():
    print(f"🔗 Llegint sitemap: {MAIN_SITEMAP_URL}")
    main_xml = fetch_xml(MAIN_SITEMAP_URL)
    product_sitemaps = get_sub_sitemaps(main_xml)

    print(f"🧭 Sitemaps trobats:")
    for sm in product_sitemaps:
        print("➡️", sm)

    all_urls = []
    for sitemap_url in product_sitemaps:
        print(f"📄 Analitzant: {sitemap_url}")
        sitemap_xml = fetch_xml(sitemap_url)
        urls = extract_product_urls_from_sitemap(sitemap_xml)
        all_urls.extend(urls)

    print(f"🔎 S'han trobat {len(all_urls)} productes")

    data = []
    for url in all_urls:
        title = scrape_title(url)
        if title:
            slug = url.strip('/').split('/')[-1]
            data.append({"url": url, "title": title, "slug": slug})

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ S'han guardat {len(data)} productes a {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
