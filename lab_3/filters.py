import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from PIL import Image
from pixel_buffer import PixelBuffer

def get_func(func):
    return {"min": np.min, "max": np.max, "median": np.median}.get(func)

def apply_filter(buffer: PixelBuffer, radius: int, process_function: str, padding_method: str = "clamp") -> PixelBuffer:
    window_size = 2 * radius + 1
    padded = buffer.create_padded_array(radius)
    h, w = padded.shape[:2]
    filtered = np.empty((h, w), dtype=np.uint8)
    func = get_func(process_function)

    windows = sliding_window_view(padded, (window_size, window_size))

    filtered = func(windows, axis=(2, 3)).astype(np.uint8)

    PixelBuffer(filtered)

    return PixelBuffer(filtered)