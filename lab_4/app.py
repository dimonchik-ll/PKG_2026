import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Лабораторная работа №4", layout="wide")
st.title("Лабораторная работа №4")

w = h = st.sidebar.slider("Размер", min_value=5, max_value=25, value=15, step=1)
grid = np.zeros((w, h))

fig, ax = plt.subplots(figsize=(8, 8))

ax.imshow(grid.T, cmap='Greys', origin='lower')

ax.set_xticks(np.arange(-0.5, w, 1), minor=True)
ax.set_yticks(np.arange(-0.5, h, 1), minor=True)
ax.grid(which="minor", color="gray", linestyle='-', linewidth=0.5)

ax.set_xticks(np.arange(0, w, 1))
ax.set_yticks(np.arange(0, h, 1))

st.pyplot(fig, width=600)