from PIL import Image

def open_image(file_path):
    try:
        img = Image.open(file_path)
        img.verify()  # Verify that it is, in fact, an image
        # Re-open the image file to reset the file pointer after verify??
        img = Image.open(file_path)
        img = img.convert("RGB")
        return img
    except (IOError, SyntaxError) as e:
        print(f"Cannot open image. Error: {e}")
        return None

# Example usage:
#file_path = 'L691_1_2022-11-04_14.11.41.ims'
file_path = 'L691_1_2022-11-04_14.11.410000.png'
image = open_image(file_path)

if image:
    print("Image opened successfully")
    image.convert("RGB")
else:
    print("Failed to open image")
