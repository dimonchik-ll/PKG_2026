import numpy as np
from pixel_buffer import PixelBuffer

def convert_to_grayscale(data: np.ndarray):
    grayscale_data = np.dot(data[..., :3], [0.299, 0.587, 0.114])
    grayscale_data = grayscale_data.astype(np.uint8)

    return grayscale_data

def create_window_sums_matrix(padded_matrix: np.ndarray, image_height: int, image_width: int, window_size: int, element_func = (lambda x : x)):
    pad_h, pad_w = padded_matrix.shape[:2]

    sat = np.zeros((pad_h + 1, pad_w + 1), dtype=np.float64)

    sat[1:, 1:] = np.cumsum(np.cumsum(element_func(padded_matrix), axis=0), axis=1)

    A = sat[0:image_height, 0:image_width]
    B = sat[0:image_height, window_size :  window_size + image_width]
    C = sat[window_size: window_size + image_height, 0:image_width]
    D = sat[window_size : window_size + image_height, window_size : window_size + image_width]

    window_sums = A + D - C - B

    return window_sums

def apply_niblak_thresholding(buffer: PixelBuffer, radius: int, k: int, padding_method: str = "clamp"):
    img_array = buffer.data
    window_size = radius * 2 + 1
    window_area = window_size ** 2
    h, w = buffer.height, buffer.width

    padded = buffer.create_padded_array(radius=radius, padding_method=padding_method)

    window_sums = create_window_sums_matrix(padded, h, w, window_size)
    window_sq_sums = create_window_sums_matrix(padded, h, w, window_size, lambda x : x ** 2)

    mean = window_sums / window_area
    mean_sq = window_sq_sums / window_area

    variance = np.clip(mean_sq - mean ** 2, 0, None)
    std = np.sqrt(variance)

    threshold = mean + k * std

    out = np.where(img_array > threshold, 255, 0).astype(np.uint8)

    return PixelBuffer(out)

def apply_sauvola_thresholding(buffer: PixelBuffer, radius: int, k: int, padding_method: str = "clamp"):
    pass