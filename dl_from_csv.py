import csv
import os
import requests

def download_images_from_csv(csv_file="images.csv", output_dir="images"):
    """
    Downloads images from URLs listed in a CSV file.

    :param csv_file: Path to the CSV file (default: "images.csv")
    :param output_dir: Directory to save downloaded images (default: "downloaded_images")
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Read the CSV file
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            image_url = row["Image URL"]
            try:
                # Extract the filename from the URL
                filename = os.path.join(output_dir, os.path.basename(image_url))

                # Download the image
                # TODO: Some of the downloaded files are not actual picture files
                if not os.path.isfile(filename):
                    response = requests.get(image_url, stream=True, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    })
                    response.raise_for_status()  # Raise an error for bad status codes

                    # Save the image
                    try:
                        with open(filename, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        print(f"Downloaded: {filename}")
                    except Exception as e:
                        print(f"Something went wrong: {e}")
                else:
                    print("file already exists")

            except requests.exceptions.RequestException as e:
                print(f"Failed to download {image_url}: {e}")

# Example usage:
download_images_from_csv()
