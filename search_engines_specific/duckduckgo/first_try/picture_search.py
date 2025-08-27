import os
import time
import requests
from datetime import datetime
from urllib.parse import urlparse, unquote
from ddgs import DDGS
import clamd

# --- For output CSV file ---
def saved_results(url, csv_file="image_search_output.csv"):
    with open(csv_file, 'a') as report_csv:
        report_csv.write(url + "\n")

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
    if basename:
        return unquote(basename)
    else:
        return fallback_name

# --- Image finder ---
def find_images(query, max_results=20, download=True, download_dir="images"):
    """Search DuckDuckGo for images and optionally download them (with ClamAV scan)."""
    image_links = []
    os.makedirs(download_dir, exist_ok=True)
    with DDGS() as ddgs:
        results = ddgs.text(f"{query} filetype:jpg OR filetype:png OR filetype:jpeg OR filetype:bmp OR filetype:gif OR filetype:tiff OR filetype:webp", max_results=max_results)
        for r in results:
            url = r.get("href", "")
            if not url:
                continue
            # Check if it's an image link
            is_image = url.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"))
            if not is_image:
                try:
                    head = requests.head(url, timeout=5, allow_redirects=True)
                    content_type = head.headers.get("Content-Type", "").lower()
                    if content_type in ("image/jpeg", "image/png"):
                        is_image = True
                except Exception:
                    continue
            if is_image:
                image_links.append(url)
    # Download + scan
    if download:
        for i, url in enumerate(image_links, 1):
            try:
                print(f"⬇️ Downloading {url}")
                r = requests.get(url, timeout=15)
                local_name = get_filename_from_url(url, f"{query}_{i}.jpg")
                filename = os.path.join(download_dir, local_name)
                if not os.path.isfile(filename):
                    with open(filename, "wb") as f:
                        f.write(r.content)
                    saved_results(url)
                else:
                    print(f"File {local_name} already exists!")
                # Scan with ClamAV
                # if not scan_file_with_clamav(filename):
                #     os.remove(filename)
                #     print(f"🗑️ Removed infected file {filename}")
                # else:
                #     print(f"✅ No viruses found: {filename}")
            except Exception as e:
                print(f"❌ Failed to download {url}: {e}")
    return image_links

# --- Main ---
if __name__ == "__main__":
    try:
        check_freshclam_date()
    except Exception as e:
        print(f"Couldn't see virus information: {e}")

    print("\nStarting process...")
    keywords = load_keywords("search_engines_specific/duckduckgo/search_words.txt")
    for kw in keywords:
        print(f"\n🔍 Searching for: {kw}")
        images = find_images(kw, max_results=100, download=True, download_dir="images")
        print(f"Found {len(images)} image links for '{kw}'")
        time.sleep(2)  # Polite delay between queries
