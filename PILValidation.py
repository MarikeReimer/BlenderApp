from PIL import Image

def open_image(file_path):
    try:
        img = Image.open(file_path)
        img.verify()  # Verify that it is, in fact, an image
        # Re-open the image file to reset the file pointer after verify(??) Workaround provided by Chat.gpt 
        img = Image.open(file_path)
        img = img.convert("RGB")
        return img
    except (IOError, SyntaxError) as e:
        print(f"Unsupported Imagetype: {e}, Please convert image stack to a sequence of png or jpg files in the directory created.  We recommended this open source tool: https://imagej.net/ij/download.html")
        #check for directory named after image
        #If it's not there,make it.
        return None

# Example usage:
file_path = 'L691_1_2022-11-04_14.11.41.ims'
#file_path = 'L691_1_2022-11-04_14.11.410000.PNG'

image = open_image(file_path)

if image:
    print(file_path,"Image stack added successfully")
    image.convert("RGB")
    #Add objects to Image group
    #Add Image group to NWBFile
    #Add to NWBFile

elif image == None:
    pass

else:
    print("Image sequence added successfully for ", file_path)

    #For all images in the stack, create a pynwb object
    #Add objects to Image group
    #Add Image group to NWBFile