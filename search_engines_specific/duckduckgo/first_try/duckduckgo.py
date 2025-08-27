from duckduckgo_search import DDGS

with DDGS() as ddgs:
    results = ddgs.text("climate change filetype:pdf", max_results=20)
    for r in results:
        print(r["href"])
