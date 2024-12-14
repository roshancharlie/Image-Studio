import numpy as np
import torch
from PIL import Image
from torchvision.transforms.functional import normalize
import torch.nn.functional as F


def resize_image(image, target_size=(1024, 1024)):
    """
    Resize the input image to the target size while maintaining RGB mode.
    """
    return image.convert('RGB').resize(target_size, Image.BILINEAR)

def preprocess_image(image):
    """
    Preprocess the image by converting it to a normalized tensor.
    """
    image_np = np.array(image)
    image_tensor = torch.tensor(image_np, dtype=torch.float32).permute(2, 0, 1)
    image_tensor = torch.unsqueeze(image_tensor, 0) / 255.0
    return normalize(image_tensor, [0.5, 0.5, 0.5], [1.0, 1.0, 1.0])


def postprocess_result(result, original_size):
    """
    Post-process the model's output to convert it into a transparent image.
    """
    result = torch.squeeze(F.interpolate(result[0][0], size=original_size, mode='bilinear'), 0)
    result = (result - result.min()) / (result.max() - result.min())
    result_np = (result * 255).cpu().data.numpy().astype(np.uint8)
    return Image.fromarray(np.squeeze(result_np))