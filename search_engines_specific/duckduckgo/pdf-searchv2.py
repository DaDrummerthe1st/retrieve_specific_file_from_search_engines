import os
import time
import requests
from datetime import datetime
from urllib.parse import urlparse, unquote
import csv

from ddgs import DDGS

# --- For output CSV file ---
def save_to_csv(pdf_urls, filename="pdfs.csv"):
    """
    Saves a list of pdf URLs to a CSV file, avoiding duplicates.
    :param pdf_urls: List of lists of pdf URLs
    :param filename: Name of the CSV file (default: "pdfs.csv")
    """
    # Read existing URLs from the file
    existing_urls = set()
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # Skip the header
            for row in reader:
                if row:  # Ensure row is not empty
                    existing_urls.add(row[0])
    except FileNotFoundError:
        pass  # File doesn't exist yet, so no existing URLs

    # Collect new unique URLs
    new_urls = set()
    for url_list in pdf_urls:
        for url in url_list:
            if url not in existing_urls:
                new_urls.add(url)

    # Write new URLs to the file
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write header only if the file is empty
        if not existing_urls:
            writer.writerow(["pdf URL"])
        for url in new_urls:
            writer.writerow([url])

    print(f"Added {len(new_urls)} new unique PDF URLs to {filename}.")


# --- Load search keywords ---
def load_keywords(filename="search_words.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]
        print(keywords)
        return keywords
    
def get_filename_from_url(url, fallback_name):
    path = urlparse(url).path
    basename = os.path.basename(path)
    if basename:  # found a filename in URL
        return unquote(basename)
    else:
        return fallback_name
    
# --- PDF finder ---
def find_pdfs(query, max_results=20):
    """Search DuckDuckGo for PDFs and output a csv-file"""
    pdf_links = []
    # os.makedirs(download_dir, exist_ok=True)

    with DDGS() as ddgs:
        results = ddgs.text(f"{query} filetype:pdf", max_results=max_results)
        for r in results:
            url = r.get("href", "")
            if not url:
                continue

            # Check if it's a PDF link
            is_pdf = url.lower().endswith(".pdf")
            ## This section looks deeper into files to find if they are indeed pdf-files, despite not .pdf
            # if not is_pdf:
            #     try:
            #         head = requests.head(url, timeout=5, allow_redirects=True)
            #         if head.headers.get("Content-Type", "").startswith("application/pdf"):
            #             is_pdf = True
            #     except Exception:
            #         continue

            if is_pdf:
                pdf_links.append(url)

    # # Download + scan
    # if download:
    #     for i, url in enumerate(pdf_links, 1):
    #         try:
    #             print(f"⬇️ Downloading {url}")
    #             r = requests.get(url, timeout=15)
                
    #             # Set the saved file name
    #             local_name = get_filename_from_url(url, f"{query}_{i}.pdf")
    #             filename = os.path.join(download_dir, local_name)

    #             if not os.path.isfile(filename):
    #                 with open(filename, "wb") as f:
    #                     f.write(r.content)
    #                 saved_results(url)
    #             else:
    #                 print(f"File {local_name} already exists!")

    #             # # This section kinda works...
    #             # # It deletes ALL files but some exceptions when trying to scan.
    #             # # Not because of find viruses but because of failures I didn't have time to troubleshoot
    #             # # Scan with ClamAV
    #             # if not scan_file_with_clamav(filename):
    #             #     os.remove(filename)
    #             #     print(f"🗑️ Removed infected file {filename}")
    #             # else:
    #             #     print(f"✅ No viruses found: {filename}")

    #         except Exception as e:
    #             print(f"❌ Failed to download {url}: {e}")

    return pdf_links

pdf_links_list = []

# --- Main ---
if __name__ == "__main__":
    # after checks
    print("Starting process...")
    keywords = load_keywords("search_engines_specific/duckduckgo/search_words.txt")

    for kw in keywords:
        print(f"\n🔍 Searching for: {kw}")
        pdfs = find_pdfs(kw, max_results=50)
        print(f"Found {len(pdfs)} PDF links for '{kw}'")
        pdf_links_list.append(pdfs)
        time.sleep(2)  # polite delay between queries

    save_to_csv(pdf_links_list)
    