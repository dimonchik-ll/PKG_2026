import numpy as np
from PIL import Image
from pixel_buffer import PixelBuffer

def get_func(func):
    return {"min": np.min, "max":np.max, "median": np.median}.get(func)

def apply_filter(buffer: PixelBuffer, radius: int, process_function: str, padding_method: str = "clamp") -> PixelBuffer:
    window_size = 2 * radius + 1
    padded = buffer.create_padded_array(radius)
    h, w = padded.shape[:2]
    filtered = np.empty((h, w), dtype=np.uint8)
    func = get_func(process_function)

    for y in range(h):
        for x in range(w):
            window = padded[y : y + window_size, x : x + window_size] 

            filtered[y, x] = func(window)

    result_buffer = PixelBuffer(filtered)

    return result_buffer