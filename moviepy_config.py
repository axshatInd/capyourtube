import os
from moviepy.config import change_settings

# Path to ImageMagick binary (adjust if installed to a different location)
magick_binary = "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"

if os.path.exists(magick_binary):
    change_settings({"IMAGEMAGICK_BINARY": magick_binary})
else:
    print(f"Warning: ImageMagick not found at {magick_binary}. Please check installation path.")