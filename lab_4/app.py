import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from algoithms import DiscreteGrid

st.set_page_config(page_title="Лабораторная работа №4", layout="wide")
st.title("Лабораторная работа №4")

size = 50
half = size // 2
discrete_grid = DiscreteGrid(size)

st.sidebar.subheader("Тип линии:")
line_type = st.sidebar.radio("line_type", ("Прямая", "Окружность", "Эллипс"), label_visibility="collapsed")

if line_type == "Прямая":
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

elif line_type == "Окружность":
    st.sidebar.subheader("Центр окружности:")
    c1, c2 = st.sidebar.columns(2)
    with c1:
        cx = st.number_input("x", min_value=-size, max_value=size - 1, value=0, step=1)
    with c2:
        cy = st.number_input("y", min_value=-size, max_value=size - 1, value=0, step=1)

    st.sidebar.subheader("Радиус:")
    r = st.sidebar.number_input("r", min_value=1, max_value=half, value=1, step=1)

    discrete_grid.bresenham_circle(cx, cy, r)
    grid = discrete_grid.get_grid()

elif line_type == "Эллипс":
    st.sidebar.subheader("Центр эллипса:")
    c1, c2 = st.sidebar.columns(2)
    with c1:
        cx = st.number_input("x", min_value=-size, max_value=size - 1, value=0, step=1)
    with c2:
        cy = st.number_input("y", min_value=-size, max_value=size - 1, value=0, step=1)

    st.sidebar.subheader("Полуоси:")
    c1, c2 = st.sidebar.columns(2)
    with c1:
        a = st.number_input("a", min_value=1, max_value=size - 1, value=1, step=1)
    with c2:
        b = st.number_input("b", min_value=1, max_value=size - 1, value=1, step=1)

    discrete_grid.castle_pitteway_ellipse(cx, cy, a, b)
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

if line_type == "Прямая":
    ax.text(x_1 - 0.25, y_1 - 0.25, "A", color='red', fontsize=8, fontweight='bold', zorder=5)
    ax.text(x_2 - 0.25, y_2 - 0.25, "B", color='red', fontsize=8, fontweight='bold', zorder=5)
else:
    ax.scatter(cx, cy, s=25, color='red', zorder=5)

st.pyplot(fig)