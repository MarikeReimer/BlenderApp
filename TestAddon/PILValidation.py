from PIL import Image
import os


from datetime import datetime
from uuid import uuid4

import numpy as np
from dateutil import tz
from dateutil.tz import tzlocal
from PIL import Image

from pynwb import NWBHDF5IO, NWBFile
from pynwb.base import Images
from pynwb.image import GrayscaleImage, ImageSeries, OpticalSeries, RGBAImage, RGBImage

nwbfile_path = os.getcwd()

session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))

nwbfile = NWBFile(
    session_description="my first synthetic recording",
    identifier=str(uuid4()),
    session_start_time=datetime.now(tzlocal()),
    experimenter=[
        "Baggins, Bilbo",
    ],
    lab="Bag End Laboratory",
    institution="University of Middle Earth at the Shire",
    experiment_description="I went on an adventure to reclaim vast treasures.",
    session_id="LONELYMTN001",
)

nwbfile

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
#file_path = 'L691_1_2022-11-04_14.11.41.ims'
file_path = 'L691_1_2022-11-04_14.11.410000.PNG'

image = open_image(file_path)

if image:
    print(file_path,"Image stack added successfully")
    image.convert("RGB")
    rgb_logo = RGBImage(
        name="test",
        data=np.array(image.convert("RGB")),
        resolution=70.0,
        description="RGB version of the PyNWB logo.",
    )
    images = Images(
        name="logo_images",
        images=[rgb_logo],
        description="A collection of logo images presented to the subject.",
    )
    nwbfile.add_acquisition(images)
    print('done')

else:
    print("Image sequence added successfully for ", file_path)

    #For all images in the stack, create a pynwb object
    #Add objects to Image group
    #Add Image group to NWBFile



with NWBHDF5IO("PILWorkaround.nwb", "w") as io:
    io.write(nwbfile)