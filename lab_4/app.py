import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from algoithms import DiscreteGrid

st.set_page_config(page_title="Лабораторная работа №4", layout="wide")
st.title("Лабораторная работа №4")

size = 50
half = size // 2
discrete_grid = DiscreteGrid(size)

st.sidebar.subheader("Точка A:")
c1, c2 = st.sidebar.columns(2)
with c1:
    x_1 = st.number_input("x_a", min_value=-size, max_value=size - 1, value=0, step=1)
with c2:
    y_1 = st.number_input("y_a", min_value=-size, max_value=size - 1, value=0, step=1)

st.sidebar.subheader("Точка B:")
c1, c2 = st.sidebar.columns(2)
with c1:
    x_2 = st.number_input("x_b", min_value=-size, max_value=size - 1, value=0, step=1)
with c2:
    y_2 = st.number_input("y_b", min_value=-size, max_value=size - 1, value=0, step=1)

algorthm = st.sidebar.radio(
    "Выберите алгоритм отрисовки",
    (
        "Пошаговый алгоритм", 
        "Алгоритм ЦДА", 
        "Алгоритм Брезенхема"
    )
)

if algorthm == "Пошаговый алгоритм":
    discrete_grid.naive_drawing_algorithm(x_1, y_1, x_2, y_2)
elif algorthm == "Алгоритм ЦДА":
    discrete_grid.dda_algorithm(x_1, y_1, x_2, y_2)
else:
    discrete_grid.bresenham_algorithm(x_1, y_1, x_2, y_2)

grid = discrete_grid.get_grid()


fig, ax = plt.subplots(figsize=(10, 10))

extent = [-half - 0.5, half - 0.5, -half - 0.5, half - 0.5]
ax.imshow(grid.T, cmap='Greys', origin='lower', extent=extent)

ax.set_xticks(np.arange(-half - 0.5, half + 0.5, 1), minor=True)
ax.set_yticks(np.arange(-half - 0.5, half + 0.5, 1), minor=True)
ax.grid(which="minor", color="gray", linestyle='-', linewidth=0.5)

ax.axhline(0, color='black', linewidth=1.5)
ax.axvline(0, color='black', linewidth=1.5)

ax.set_xticks(np.arange(-half, half, 5))
ax.set_yticks(np.arange(-half, half, 5))
ax.grid(False, which="major")

ax.text(x_1 - 0.25, y_1 - 0.25, "A", color='red', fontsize=8, fontweight='bold', zorder=5)
ax.text(x_2 - 0.25, y_2 - 0.25, "B", color='red', fontsize=8, fontweight='bold', zorder=5)

st.pyplot(fig)