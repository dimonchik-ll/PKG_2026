import streamlit as st
from PIL import Image
import numpy as np
from local_thresholding import convert_to_grayscale, apply_niblack_thresholding
from filters import apply_filter
from pixel_buffer import PixelBuffer

st.image("test_images/4_adaptive_extreme_shadow.png")

img = Image.open("test_images/4_adaptive_extreme_shadow.png").convert("RGB")
data = np.array(img)
buffer = PixelBuffer(convert_to_grayscale(data))

res_buffer = apply_niblack_thresholding(buffer, 30, -0.1)

st.image(res_buffer.to_Image())