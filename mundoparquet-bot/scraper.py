import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configuració del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/scraper.log'),  # Guardem el log al disc persistent
        logging.StreamHandler()
    ]
)

SITEMAP_URL = "https://www.mundoparquet.com/sitemap.xml"
OUTPUT_FILE = "/app/mundoparquet_data.json"  # Guardem el JSON al disc persistent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def create_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def setup_selenium():
    options = Options()
    options.headless = True
    options.add_argument(f'user-agent={HEADERS["User-Agent"]}')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    return driver

def fetch_sitemap(url, session):
    logging.info(f"Intentant descarregar el sitemap: {url}")
    try:
        response = session.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
        logging.info("Sitemap descarregat correctament")
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error al descarregar el sitemap: {e}")
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

def scrape_product_data(url, driver):
    logging.info(f"Scraping dades de: {url}")
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        data = {"url": url}
        
        title_tag = soup.find("title") or soup.find("h1")
        data["title"] = title_tag.text.strip() if title_tag else None

        price_tag = soup.find(class_=["price", "product-price", "special-price", "regular-price"])
        data["price"] = price_tag.text.strip() if price_tag else None

        desc_tag = soup.find(class_=["product-description", "description", "product-details"])
        data["description"] = desc_tag.text.strip() if desc_tag else None

        images = [img["src"] for img in soup.find_all("img", src=True) if "product" in img["src"].lower()]
        data["images"] = images

        specs = {}
        spec_table = soup.find(class_=["product-attributes", "technical-specs"])
        if spec_table:
            for row in spec_table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 2:
                    specs[cells[0].text.strip()] = cells[1].text.strip()
        data["specifications"] = specs

        breadcrumbs = [crumb.text.strip() for crumb in soup.select(".breadcrumbs a")]
        data["categories"] = breadcrumbs

        brand_tag = soup.find(class_=["brand", "manufacturer"])
        data["brand"] = brand_tag.text.strip() if brand_tag else None

        if not data["title"] or "404" in data["title"] or "Error" in data["title"]:
            return None

        data["slug"] = url.strip('/').split('/')[-1]
        logging.info(f"Dades extretes per {url}: {data['title']}")
        return data
    except Exception as e:
        logging.warning(f"Error al scrapejar {url}: {e}")
        return None

def scrape_category_data(url, driver):
    logging.info(f"Scraping dades de categoria: {url}")
    try:
        driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        data = {"url": url}
        title_tag = soup.find("title") or soup.find("h1")
        data["title"] = title_tag.text.strip() if title_tag else None
        desc_tag = soup.find(class_=["category-description", "description"])
        data["description"] = desc_tag.text.strip() if desc_tag else None
        return data
    except Exception as e:
        logging.warning(f"Error al scrapejar categoria {url}: {e}")
        return None

def scrape_product_links(category_url, driver):
    logging.info(f"Explorant categoria: {category_url}")
    try:
        driver.get(category_url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_links = [
            a['href'] for a in soup.select('a[href*="/catalog/product/view"], a[href*="/rodapie/"], a[href*="/puertas/"]')
            if a.get('href') and is_product_url(a['href'])
        ]
        logging.info(f"Trobades {len(product_links)} URLs de producte a {category_url}")
        return product_links
    except Exception as e:
        logging.warning(f"Error al scrapejar categoria {category_url}: {e}")
        return []

def is_product_url(url):
    logging.debug(f"Comprovant si {url} és una URL de producte")
    if "/catalog/product/view" in url:
        return True
    if "/rodapie/" in url and url.count('/') >= 5:
        return True
    if "/puertas/" in url and url.count('/') >= 5:
        return True
    return False

def main():
    logging.info("Iniciant el procés de scraping")
    session = create_session()
    driver = setup_selenium()
    try:
        xml = fetch_sitemap(SITEMAP_URL, session)
        urls = extract_all_urls(xml)
        
        logging.info(f"🔎 S'han trobat {len(urls)} URLs al sitemap")
        logging.info("📋 Primeres 10 URLs:")
        for u in urls[:10]:
            logging.info(f"➡️ {u}")

        product_urls = [u for u in urls if is_product_url(u)]
        
        category_urls = [
            u for u in urls 
            if any(cat in u for cat in ['/suelos-laminados/', '/vinilo/', '/rodapie/', '/puertas/'])
            and not is_product_url(u)
        ]
        logging.info(f"🗂️ Trobades {len(category_urls)} URLs de categories")

        for category_url in category_urls[:20]:
            product_urls.extend(scrape_product_links(category_url, driver))
            time.sleep(2)
        
        product_urls = list(set(product_urls))
        logging.info(f"🧪 URLs de producte filtrades: {len(product_urls)}")
        logging.info("📋 Primeres 10 URLs de productes (si n'hi ha):")
        for u in product_urls[:10]:
            logging.info(f"➡️ {u}")

        products_data = []
        for url in product_urls[:50]:
            product_data = scrape_product_data(url, driver)
            if product_data:
                products_data.append(product_data)
            time.sleep(2)

        categories_data = []
        for url in category_urls[:20]:
            category_data = scrape_category_data(url, driver)
            if category_data:
                categories_data.append(category_data)
            time.sleep(2)

        output_data = {
            "products": products_data,
            "categories": categories_data
        }
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        logging.info(f"✅ S'han guardat {len(products_data)} productes i {len(categories_data)} categories a {OUTPUT_FILE}")

    except Exception as e:
        logging.error(f"Error en el procés principal: {e}")
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
