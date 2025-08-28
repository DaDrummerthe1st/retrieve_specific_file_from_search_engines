###### This file does not work since DuckDuckGo do not find actual video-files, just equivalence to youtube-links

import subprocess

from ddgs import DDGS
import csv

# --- constants ---
list_of_file_types = [
    ".mp4",    # MPEG-4 Part 14
    ".mov",    # QuickTime File Format
    ".avi",    # Audio Video Interleave
    #".mkv",    # Matroska Multimedia Container
    ".flv",    # Flash Video Format
    ".wmv",    # Windows Media Video
    ".webm",   # WebM (open, royalty-free format)
    ".m4v",    # MPEG-4 Visual Bitstream
    ".ogv",    # Ogg Video Format
    ".3gp",    # 3GPP Multimedia File
    ".mpeg",   # MPEG Video File
    ".mpg",    # MPEG Video File
    #".ts",     # MPEG Transport Stream
    #".vob",    # DVD Video Object
    #".m2ts",   # MPEG-2 Transport Stream
]

# --- Load search keywords ---
def load_keywords(filename="search_words.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f if line.strip()]
        print(keywords)
        return keywords

def fetch_video_urls(query, max_results=20):
    """
    Fetches direct video URLs using DuckDuckGo Search.

    :param query: Search query (e.g., "summer beer")
    :param max_results: Maximum number of results to fetch (default: 10)
    :return: List of direct video URLs
    """
    try: 
        with DDGS() as ddgs:
            ddgs_videos_gen = ddgs.videos(
                query,
                region = "us-en",
                safesearch = "off",
                timelimit = None,
                resolution = None,
                duration = "short",
                license_videos = "creativeCommon",
                max_results = max_results
            )
            video_urls = [result for result in ddgs_videos_gen]
        return video_urls
    except Exception as e:
        print(f"Something went wrong: {e}")
        return None

def save_to_csv(video_urls, filename="videos.csv"):
    """
    Saves a list of video URLs to a CSV file.

    :param video_urls: List of video URLs
    :param filename: Name of the CSV file (default: "videos.csv")
    """
    if video_urls is not None:
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["video URL"])
            for url in video_urls:
                writer.writerow([url])
        print(f"Wrote {len(video_urls)} video URLs to {filename}.")
    
    # # clean up the file
    # try:
    #     subprocess.run(f"sort -u", stdin=filename, stdout="videos_clean.csv")
    # except Exception as e:
    #     print(f"Something went wrong: {e}")

if __name__ == "__main__":
    keywords = load_keywords("search_engines_specific/duckduckgo/search_words.txt")
    for kw in keywords:
        print(f"searching for: {kw}")
        for type in list_of_file_types:
            search_term = kw + " " + type + "-youtube.com -tiktok.com '.avi'"
            video_urls = fetch_video_urls(search_term, max_results=50)
            save_to_csv(video_urls)
