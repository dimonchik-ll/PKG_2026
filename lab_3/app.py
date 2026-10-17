import streamlit as st
from PIL import Image
import numpy as np
from local_thresholding import convert_to_grayscale
from filters import apply_filter
from pixel_buffer import PixelBuffer

st.image("test_images/ава.jpg")

img = Image.open("test_images/ава.jpg").convert("RGB")
data = np.array(img)
buffer = PixelBuffer(convert_to_grayscale(data))

res_buffer = apply_filter(buffer, 7, "min")

st.image(res_buffer.to_Image())