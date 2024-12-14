from PIL import Image
from remove_background.utils import change_background, matte


def image_background_removal(image, bg_color):
    hexmap = {
        "Transparent (PNG)": "#000000",
        "Black": "#000000",
        "White": "#FFFFFF",
        "Green": "#22EE22",
        "Red": "#EE2222",
        "Blue": "#2222EE",
    }
    alpha = 0.0 if bg_color == "Transparent (PNG)" else 1.0
    img_matte = matte(image)
    img_output = change_background(image, img_matte, background_alpha=alpha,
                                   background_hex=hexmap[bg_color])

    return img_output


# Example usage:
input_image_path = "model5.jpg"
background_color = "White"  # Choose the desired background color

input_image = Image.open(input_image_path)
output_image = image_background_removal(input_image, background_color)
output_image = image_background_removal(output_image, background_color)
output_image.save("output_image_1.png")

