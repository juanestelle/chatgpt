import requests
import xml.etree.ElementTree as ET

SITEMAP_URL = "https://www.mundoparquet.com/sitemap.xml"

def fetch_sitemap(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def extract_urls(xml_content):
    root = ET.fromstring(xml_content)
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [url.find('ns:loc', ns).text for url in root.findall('ns:url', ns)]
    return urls

def main():
    sitemap = fetch_sitemap(SITEMAP_URL)
    urls = extract_urls(sitemap)
    print(f"🔍 S'han trobat {len(urls)} URLs al sitemap")
    print("📋 Primeres 10 URLs:")
    for u in urls[:10]:
        print("-", u)

if __name__ == "__main__":
    main()
