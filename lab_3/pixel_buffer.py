import numpy as np
from PIL import Image

class PixelBuffer:
    def __init__(self, image_array: np.ndarray):
        self.data = image_array
        self.height, self.width = image_array.shape[:2]

    def create_padded_array(self, radius: int, padding_method: str = "clamp"):
        pad_h = self.height + radius * 2
        pad_w = self.width + radius * 2
        padded = np.empty((pad_h, pad_w), dtype=np.uint8)

        for y in range(pad_h):
            for x in range(pad_w):
                if y < radius:
                    src_y = 0
                elif y >= self.height + radius:
                    src_y = self.height - 1 
                else:
                    src_y = y - radius

                if x < radius:
                    src_x = 0
                elif x >= self.width + radius:
                    src_x = self.width - 1 
                else:
                    src_x = x - radius

                padded[y, x] = self.data[src_y, src_x]

        return padded

    def to_Image(self):
        return Image.fromarray(self.data)