import os
from PIL import Image

def resize_and_crop(image_path, target_size=(240, 180)):
    """
    Create a thumbnail using center-cropping
    Based on ChatGPT reponse https://chat.openai.com/share/4367ef05-63b6-4d6c-b1e2-df18a91307f3

    Parameters
    ----------
    :image_path (str):
        relative path to the full size image
    """
    try:
        # Open an image file
        with Image.open(image_path) as im:

            # Calculate the aspect ratio
            src_width, src_height = im.size
            target_width, target_height = target_size
            src_aspect = src_width / src_height
            target_aspect = target_width / target_height

            # Resize while keeping the aspect ratio
            if src_aspect > target_aspect:
                # If source aspect ratio is greater, set the height to the target height
                new_height = target_height
                new_width = int(new_height * src_aspect)
            else:
                # Otherwise, set the width to the target width
                new_width = target_width
                new_height = int(new_width / src_aspect)

            resized_img = im.resize((new_width, new_height), Image.ANTIALIAS)

            # Calculate the position to crop the image
            left = (resized_img.width - target_width)/2
            top = (resized_img.height - target_height)/2
            right = (resized_img.width + target_width)/2
            bottom = (resized_img.height + target_height)/2

            # Crop the center of the image
            cropped_img = resized_img.crop((left, top, right, bottom))

            # Split the file name and its extension
            filename, extension = os.path.splitext(image_path)

            # Save the cropped image to a new file
            thumbnail_filename = f"{filename}_tn{extension}"
            print(thumbnail_filename)
            cropped_img.save(thumbnail_filename, "JPEG")

            print(f"Thumbnail saved as {thumbnail_filename} \n")

    except FileNotFoundError as e:
        print(f"The file {image_path} could not be found. \n")
    except Exception as e:
        print(f"An error occurred: {str(e)} \n")