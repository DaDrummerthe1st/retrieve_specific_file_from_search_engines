import requests

def download_image(url, save_path):
    headers = {
        'User-Agent': 'MyImageDownloader/1.0 (https://example.com; joakim@example.com) Python/3.11'
    }
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Image successfully downloaded and saved to {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the image: {e}")

# Example usage:
image_url = "https://upload.wikimedia.org/wikipedia/pt/2/21/SKOL-SUMMER-ON.jpg"
save_path = "../../images/thisisnew.jpg"
download_image(image_url, save_path)
