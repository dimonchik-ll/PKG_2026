import numpy as np
from PIL import Image

class PixelBuffer:
    def __init__(self, image_array: np.ndarray):
        self.data = image_array
        self.height, self.width = image_array.shape[:2]

    def create_padded_array(self, radius: int, padding_method: str = "Clamp", rgb_cahnnels: bool = False):
        pad_h = self.height + radius * 2
        pad_w = self.width + radius * 2

        if not rgb_cahnnels:
            padded = np.empty((pad_h, pad_w), dtype=np.uint8)
        else:
            padded = np.empty((pad_h, pad_w, 3), dtype=np.uint8)

        padded[radius : radius + self.height, radius : radius + self.width] = self.data

        if padding_method == "Clamp":
            for y in range(radius):
                padded[y, radius : radius + self.width] = self.data[0, :]
                padded[pad_h - y - 1, radius : radius + self.width] = self.data[-1, :]

            for x in range(radius):
                padded[:, x] = padded[:, radius]
                padded[:, pad_w - x - 1] = padded[:, pad_w -radius - 1]

        else:
            for y in range(radius):
                padded[y, radius : radius + self.width] = self.data[radius - y, :]
                padded[pad_h - y - 1, radius : radius + self.width] = self.data[-radius + y - 1, :]

            for x in range(radius):
                padded[:, x] = padded[:, 2 * radius - x]
                padded[:, pad_w - x - 1] = padded[:, -2 * radius + x - 1]

        return padded