import numpy as np
from pixel_buffer import PixelBuffer
from numpy.lib.stride_tricks import sliding_window_view

def convert_to_grayscale(data: np.ndarray):
    grayscale_data = np.dot(data[..., :3], [0.299, 0.587, 0.114])
    grayscale_data = grayscale_data.astype(np.uint8)

    return grayscale_data

def apply_niblack_thresholding(buffer: PixelBuffer, radius: int, k: int):
    img_array = buffer.data
    window_size = radius * 2 + 1
    window_area = window_size ** 2
    h, w = buffer.height, buffer.width

    padded = buffer.create_padded_array(radius=radius)
    pad_h, pad_w = padded.shape[:2]

    sat = np.zeros((pad_h + 1, pad_w + 1), dtype=np.float64)
    sat_sq = np.zeros_like(sat)

    sat[1:, 1:] = np.cumsum(np.cumsum(padded, axis=0), axis=1)
    sat_sq[1:, 1:] = np.cumsum(np.cumsum(padded ** 2, axis=0), axis=1)

    A = sat[0:h, 0:w]
    B = sat[0:h, window_size :  window_size + w]
    C = sat[window_size: window_size + h, 0:w]
    D = sat[window_size : window_size + h, window_size : window_size + w]

    A_sq = sat_sq[0:h, 0:w]
    B_sq = sat_sq[0:h, window_size :  window_size + w]
    C_sq = sat_sq[window_size: window_size + h, 0:w]
    D_sq = sat_sq[window_size : window_size + h, window_size : window_size + w]

    window_sums = A + D - C - B

    window_sq_sums = A_sq + D_sq - C_sq - B_sq

    mean = window_sums / window_area
    mean_sq = window_sq_sums / window_area

    variance = np.clip(mean_sq - mean ** 2, 0, None)
    std = np.sqrt(variance)

    threshold = mean + k * std

    out = np.where(img_array > threshold, 255, 0).astype(np.uint8)

    return PixelBuffer(out)