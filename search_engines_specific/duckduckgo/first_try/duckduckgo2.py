import os
import requests
from ddgs import DDGS

def find_pdfs(query, max_results=20, download=False, download_dir="pdfs"):
    """Search DuckDuckGo for PDFs and optionally download them."""
    pdf_links = []

    # DuckDuckGo search
    with DDGS() as ddgs:
        results = ddgs.text(f"{query} filetype:pdf", max_results=max_results)
        for r in results:
            url = r.get("href", "")
            if url.lower().endswith(".pdf"):
                pdf_links.append(url)
            else:
                # Some links don’t end with .pdf, so we HEAD check
                try:
                    head = requests.head(url, timeout=5, allow_redirects=True)
                    if head.headers.get("Content-Type", "").startswith("application/pdf"):
                        pdf_links.append(url)
                except Exception:
                    continue

    # Download if requested
    if download:
        os.makedirs(download_dir, exist_ok=True)
        for i, url in enumerate(pdf_links, 1):
            try:
                print(f"Downloading {url}")
                r = requests.get(url, timeout=15)
                filename = os.path.join(download_dir, f"doc_{i}.pdf")
                with open(filename, "wb") as f:
                    f.write(r.content)
            except Exception as e:
                print(f"❌ Failed to download {url}: {e}")

    return pdf_links


if __name__ == "__main__":
    query = "machine learning"
    pdfs = find_pdfs(query, max_results=30, download=False)

    print("\nFound PDF links:")
    for link in pdfs:
        print(link)
