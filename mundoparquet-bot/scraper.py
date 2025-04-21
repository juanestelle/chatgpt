import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import logging
import time

# Configuració del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),  # Guarda logs en un fitxer
        logging.StreamHandler()  # Mostra logs a la consola
    ]
)

SITEMAP_URL = "https://www.mundoparquet.com/sitemap.xml"
OUTPUT_FILE = "products_data.json"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_sitemap(url):
    logging.info(f"Intentant descarregar el sitemap: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        logging.info("Sitemap descarregat correctament")
        return response.text
    except requests.exceptions.HTTPError as e:
        logging.error(f"Error HTTP al descarregar el sitemap: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logging.error(f"Error de xarxa al descarregar el sitemap: {e}")
        raise
    except Exception as e:
        logging.error(f"Error inesperat al descarregar el sitemap: {e}")
        raise

def extract_all_urls(xml_content):
    logging.info("Extraient URLs del sitemap")
    try:
        root = ET.fromstring(xml_content)
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [url.find('ns:loc', ns).text for url in root.findall('ns:url', ns)]
        logging.info(f"S'han trobat {len(urls)} URLs")
        return urls
    except ET.ParseError as e:
        logging.error(f"Error al parsejar el XML del sitemap: {e}")
        raise
    except Exception as e:
        logging.error(f"Error inesperat al processar el sitemap: {e}")
        raise

def scrape_title(url):
    logging.info(f"Scraping títol de: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find("title")
        title = title_tag.text.strip() if title_tag else None
        logging.info(f"Títol trobat: {title}")
        return title
    except requests.exceptions.RequestException as e:
        logging.warning(f"Error al scrapejar {url}: {e}")
        return None
    except Exception as e:
        logging.warning(f"Error inesperat al scrapejar {url}: {e}")
        return None

def is_product_url(url):
    logging.debug(f"Comprovant si {url} és una URL de producte")
    # Patró 1: URLs amb /catalog/product/view
    if "/catalog/product/view" in url:
        return True
    # Patró 2 i 3: URLs amb molts segments i noms específics
    segments = url.strip('/').split('/')
    if len(segments) > 4 and not any(
        keyword in url for keyword in [
            '/marcas-', '/gamas/', '/resistente-al-agua/',
            '/suelos-laminados$', '/vinilo$', '/tarimas-flotantes$',
            '/puertas$', '/rodapie$'
        ]
    ):
        return True
    return False

def main():
    logging.info("Iniciant el procés de scraping")
    try:
        # Descarrega el sitemap
        xml = fetch_sitemap(SITEMAP_URL)
        
        # Extreu URLs
        urls = extract_all_urls(xml)
        
        logging.info(f"🔎 S'han trobat {len(urls)} URLs al sitemap")
        logging.info("📋 Primeres 10 URLs:")
        for u in urls[:10]:
            logging.info(f"➡️ {u}")

        # Filtra URLs de productes (limita a 50 per fer proves ràpides)
        product_urls = [u for u in urls if is_product_url(u)]
        logging.info(f"🧪 URLs de producte filtrades: {len(product_urls)}")
        logging.info("📋 Primeres 10 URLs de productes (si n
