#!/usr/bin/env python3
import os
import time
import requests
import clamd
from datetime import datetime
from ddgs import DDGS

# ----------------------------
# ClamAV Setup
# ----------------------------
def get_clamav_info():
    """Print ClamAV version and database date."""
    try:
        cd = clamd.ClamdUnixSocket()  # adjust if using TCP
        version = cd.version()
        if version:
            print(f"🔎 ClamAV version info: {version}")
        else:
            print("⚠️ Could not retrieve ClamAV version info.")

        # Check database date freshness
        dbstat = cd.stats()
        if "updated" in dbstat:
            print(f"✅ Virus DB is up-to-date ({dbstat['updated']})")
        else:
            print("⚠️ Could not determine DB update date.")
        return cd
    except Exception as e:
        print(f"❌ Failed to connect to ClamAV: {e}")
        return None


def scan_file_with_clamav(cd, filepath: str) -> bool:
    """
    Returns True if file is clean, False if infected.
    Raises RuntimeError if ClamAV scan failed.
    """
    if cd is None:
        raise RuntimeError("ClamAV connection not available")

    try:
        result = cd.scan(filepath)
        if not result:
            raise RuntimeError(f"No result from ClamAV for {filepath}")

        status = list(result.values())[0][0]

        if status == "OK":
            return True
        elif status == "FOUND":
            print(f"⚠️ Virus detected in {filepath}")
            return False
        else:
            raise RuntimeError(f"Unexpected ClamAV response: {status}")
    except Exception as e:
        raise RuntimeError(f"ClamAV scan error for {filepath}: {e}")


# ----------------------------
# PDF Downloader
# ----------------------------
def download_file(url, download_dir="pdfs"):
    os.makedirs(download_dir, exist_ok=True)
    local_filename = os.path.join(download_dir, os.path.basename(url.split("?")[0]))

    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            f.write(r.content)
        return local_filename
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return None


# ----------------------------
# Search & Process
# ----------------------------
def find_pdfs(keyword, cd, max_results=10, delay=3, download=True, download_dir="pdfs"):
    pdf_files = []
    with DDGS() as ddgs:
        for r in ddgs.text(keyword, max_results=max_results):
            url = r.get("href") or r.get("url")
            if url and url.lower().endswith(".pdf"):
                print(f"⬇️ Downloading {url}")
                filepath = download_file(url, download_dir=download_dir)
                if not filepath:
                    continue

                try:
                    is_clean = scan_file_with_clamav(cd, filepath)
                    if not is_clean:
                        os.remove(filepath)
                        print(f"🗑️ Removed infected file {filepath}")
                    else:
                        print(f"✅ File is clean: {filepath}")
                        pdf_files.append(filepath)
                except RuntimeError as e:
                    print(f"❌ {e}")
                    print(f"⚠️ Keeping file despite scan error: {filepath}")
                    pdf_files.append(filepath)

                time.sleep(delay)  # delay between downloads
    return pdf_files


# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    print("\n🚀 Starting process...")

    # Initialize ClamAV
    cd = get_clamav_info()

    # Load keywords from external txt
    with open("search_engines_specific/duckduckgo/search_words.txt", "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]
    print(f"Loaded keywords: {keywords}\n")

    # Run searches
    for kw in keywords:
        print(f"\n🔍 Searching for: {kw}")
        pdfs = find_pdfs(kw, cd, max_results=20, download=True, download_dir="pdfs")
        print(f"📂 Retrieved {len(pdfs)} PDFs for keyword '{kw}'")
