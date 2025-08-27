import os
import time
import requests
from datetime import datetime
from urllib.parse import urlparse, unquote

from ddgs import DDGS
import clamd

# --- For output CSV file ---
def saved_results(url, csv_file="pdf_search_output.csv"):
    with open(csv_file, 'a') as report_csv:
        report_csv.write(url)


# --- Check Virusdefinition ---
def check_freshclam_date():
    try:
        cd = clamd.ClamdUnixSocket()
        pong = cd.ping()
        if pong == "PONG":
            print("✅ ClamAV daemon is running and reachable.")
    except Exception as e:
        print(f"❌ Could not connect to ClamAV daemon: {e}")

    cd = clamd.ClamdUnixSocket()
    version_str = cd.version()
    print(f"🔎 ClamAV version info: {version_str}")

    # Example string: "ClamAV 1.3.0/27052/Tue Aug 27 11:23:00 2025"
    parts = version_str.split("/")
    if len(parts) >= 3:
        date_str = parts[2].strip()
        try:
            db_date = datetime.strptime(date_str, "%a %b %d %H:%M:%S %Y")
            age_days = (datetime.now() - db_date).days
            if age_days > 7:
                print(f"⚠️ Virus DB is {age_days} days old! Run `freshclam`.")
            else:
                print(f"✅ Virus DB is up-to-date ({db_date})")
        except Exception as e:
            print(f"❌ Could not parse DB date: {e}")

# --- Load search keywords ---
def load_keywords(filename="search_words.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]
        print(keywords)
        return keywords

# --- ClamAV scanner ---
def scan_file_with_clamav(filepath):
    try:
        cd = clamd.ClamdUnixSocket()
        result = cd.scan(filepath)
        if result:
            status = result[filepath][0]
            if status == 'FOUND':
                print(f"⚠️ Virus found in {filepath}: {result[filepath][1]}")
                return False
        return True
    except Exception as e:
        print(f"❌ ClamAV scan failed: {e}")
        return False
    
def get_filename_from_url(url, fallback_name):
    path = urlparse(url).path
    basename = os.path.basename(path)
    if basename:  # found a filename in URL
        return unquote(basename)
    else:
        return fallback_name

# --- PDF finder ---
def find_pdfs(query, max_results=20, download=True, download_dir="pdfs"):
    """Search DuckDuckGo for PDFs and optionally download them (with ClamAV scan)."""
    pdf_links = []
    os.makedirs(download_dir, exist_ok=True)

    with DDGS() as ddgs:
        results = ddgs.text(f"{query} filetype:pdf", max_results=max_results)
        for r in results:
            url = r.get("href", "")
            if not url:
                continue

            # Check if it's a PDF link
            is_pdf = url.lower().endswith(".pdf")
            if not is_pdf:
                try:
                    head = requests.head(url, timeout=5, allow_redirects=True)
                    if head.headers.get("Content-Type", "").startswith("application/pdf"):
                        is_pdf = True
                except Exception:
                    continue

            if is_pdf:
                pdf_links.append(url)

    # Download + scan
    if download:
        for i, url in enumerate(pdf_links, 1):
            try:
                print(f"⬇️ Downloading {url}")
                r = requests.get(url, timeout=15)
                
                # Set the saved file name
                local_name = get_filename_from_url(url, f"{query}_{i}.pdf")
                filename = os.path.join(download_dir, local_name)

                if not os.path.isfile(filename):
                    with open(filename, "wb") as f:
                        f.write(r.content)
                    saved_results(url)
                else:
                    print(f"File {local_name} already exists!")

                # # This section kinda works...
                # # It deletes ALL files but some exceptions when trying to scan.
                # # Not because of find viruses but because of failures I didn't have time to troubleshoot
                # # Scan with ClamAV
                # if not scan_file_with_clamav(filename):
                #     os.remove(filename)
                #     print(f"🗑️ Removed infected file {filename}")
                # else:
                #     print(f"✅ No viruses found: {filename}")

            except Exception as e:
                print(f"❌ Failed to download {url}: {e}")

    return pdf_links

# --- Main ---
if __name__ == "__main__":
    try:
        check_freshclam_date()
    except Exception as e:
        print(f"Couldn't see virus information: {e}")
    
    # after checks
    print("")
    print("Starting process...")
    keywords = load_keywords("search_engines_specific/duckduckgo/search_words.txt")

    for kw in keywords:
        print(f"\n🔍 Searching for: {kw}")
        pdfs = find_pdfs(kw, max_results=50, download=True, download_dir="pdfs")

        print(f"Found {len(pdfs)} PDF links for '{kw}'")
        time.sleep(2)  # polite delay between queries
