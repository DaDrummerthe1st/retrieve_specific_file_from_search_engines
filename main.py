import requests
from bs4 import BeautifulSoup

def find_pdfs(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    pdf_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.pdf')]
    return pdf_links

# Example usage
pdf_links = find_pdfs("https://google.com")
for link in pdf_links:
    print(link)
