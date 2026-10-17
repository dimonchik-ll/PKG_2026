import numpy as np

def convert_to_grayscale(data: np.ndarray):
    grayscale_data = np.dot(data[..., :3], [0.299, 0.587, 0.114])
    grayscale_data = grayscale_data.astype(np.uint8)

    return grayscale_data