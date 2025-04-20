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
