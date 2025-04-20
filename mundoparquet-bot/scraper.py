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
    urls = [
        url.find('ns:loc', ns).text
        for url in root.findall('ns:url', ns)
        if url.find('ns:loc', ns) is not None
    ]
    product_urls = [
