from ddgs import DDGS
import csv

# --- Load search keywords ---
def load_keywords(filename="search_words.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]
        print(keywords)
        return keywords

def fetch_image_urls(query, max_results=20):
    """
    Fetches direct image URLs using DuckDuckGo Search.

    :param query: Search query (e.g., "summer beer")
    :param max_results: Maximum number of results to fetch (default: 10)
    :return: List of direct image URLs
    """
    with DDGS() as ddgs:
        ddgs_images_gen = ddgs.images(
            query,
            region="wt-wt",
            safesearch="moderate",
            size=None,
            color=None,
            type_image=None,
            layout=None,
            license_image=None,
            max_results=max_results,
        )
        image_urls = [result["image"] for result in ddgs_images_gen]
    return image_urls

def save_to_csv(image_urls, filename="images.csv"):
    """
    Saves a list of image URLs to a CSV file.

    :param image_urls: List of image URLs
    :param filename: Name of the CSV file (default: "images.csv")
    """
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Image URL"])
        for url in image_urls:
            writer.writerow([url])
    print(f"Saved {len(image_urls)} image URLs to {filename}.")

if __name__ == "__main__":
    keywords = load_keywords("search_engines_specific/duckduckgo/search_words.txt")


    for kw in keywords:
        print(f"searching for: {kw}")
        image_url = fetch_image_urls(kw, max_results=50)
        save_to_csv(image_url)
