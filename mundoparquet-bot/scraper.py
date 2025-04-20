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

def extract_product_urls(xml_content):
    root = ET.fromstring(xml_content)
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [url.find('ns:loc', ns).text for url in root.findall('ns:url', ns)]
    return [u for u in urls if "/catalog/product/view" in u]

def scrape_title(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find("title").text.strip()
        return title
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def main():
    sitemap = fetch_sitemap(SITEMAP_URL)
    urls = extract_product_urls(sitemap)
    data = []

    for url in urls:
        title = scrape_title(url)
        if title:
            slug = url.strip('/').split('/')[-1]
            data.append({"url": url, "title": title, "slug": slug})

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ S'han guardat {len(data)} productes a {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
print("✅ Productes extrets:")
print(json.dumps(products, indent=2, ensure_ascii=False))
