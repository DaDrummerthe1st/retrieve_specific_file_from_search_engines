import os
from PIL import Image
from PIL.ExifTags import TAGS

def get_exif_data(image_path):
    """
    Extracts EXIF data from an image file.

    :param image_path: Path to the image file
    :return: Dictionary of EXIF data
    """
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data:
            exif = {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
            return exif
        else:
            return {"Error": "No EXIF data found"}
    except Exception as e:
        return {"Error": str(e)}

def extract_exif_from_directory(directory):
    """
    Scans a directory for image files and extracts EXIF data from each.

    :param directory: Path to the directory containing image files
    """
    # Supported image file extensions
    image_extensions = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.webp')

    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.lower().endswith(image_extensions):
            print(f"\nExtracting EXIF data from: {filename}")
            exif_data = get_exif_data(file_path)
            for tag, value in exif_data.items():
                print(f"{tag}: {value}")

# Example usage:
directory = "images"  # Replace with your directory path
extract_exif_from_directory(directory)