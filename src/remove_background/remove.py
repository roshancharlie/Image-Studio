import torch
from huggingface_hub import hf_hub_download
from model import BriaRMBG
from PIL import Image
from .utils import resize_image, preprocess_image, postprocess_result


class BackgroundRemover:
    def __init__(self):
        """
        Load the BriaRMBG model and set it to evaluation mode.
        """
        self.model = BriaRMBG()
        model_path = hf_hub_download("briaai/RMBG-1.4", 'model.pth')

        if torch.cuda.is_available():
            self.model.load_state_dict(torch.load(model_path, weights_only=True))
            self.model = self.model.cuda()
        else:
            self.model.load_state_dict(torch.load(model_path, map_location="cpu"))

        self.model.eval()

    def remove_background(self, input_image, background_color="transparent"):
        """
        Perform background removal on the input image with the specified background color.
        """
        original_image = Image.fromarray(input_image)
        original_size = original_image.size

        resized_image = resize_image(original_image)
        preprocessed_image = preprocess_image(resized_image)

        if torch.cuda.is_available():
            preprocessed_image = preprocessed_image.cuda()

        with torch.no_grad():
            result = self.model(preprocessed_image)

        mask_image = postprocess_result(result, original_size)
        if mask_image.size != original_size:
            if mask_image.size == (original_size[1], original_size[0]):
                mask_image = mask_image.transpose(Image.TRANSPOSE)
            else:  # Resize if necessary
                mask_image = mask_image.resize(original_size, Image.LANCZOS)

        background_map = {
            "transparent": ("RGBA", (0, 0, 0, 0)),
            "black": ("RGB", (0, 0, 0)),
            "white": ("RGB", (255, 255, 255)),
            "red": ("RGB", (255, 0, 0)),
            "green": ("RGB", (0, 255, 0))
        }

        if background_color not in background_map:
            raise ValueError("Unsupported background color")

        mode, color = background_map[background_color]
        output_img = Image.new(mode, mask_image.size, color)

        print(f"Original Image Size: {original_image.size}")
        print(f"Mask Image Size: {mask_image.size}")
        output_img.paste(original_image, mask=mask_image)
        return output_img


