import streamlit as st
from PIL import Image
import numpy as np
from local_thresholding import convert_to_grayscale, apply_niblak_thresholding, apply_sauvola_thresholding
from filters import apply_filter
from pixel_buffer import PixelBuffer

st.set_page_config(page_title="Лабораторная работа №3", layout="wide")
st.title("Лабораторная работа №3 — Вариант 15")

uploaded = st.sidebar.file_uploader("Загрузите изображение (PNG, JPG, BMP)", type=["png", "jpg", "jpeg", "bmp"])
if uploaded is not None:
    input_image = Image.open(uploaded).convert("RGB")
    input_np = np.array(input_image, dtype=np.uint8)
    input_rgb_buffer = PixelBuffer(input_np)
    grayscale_np = convert_to_grayscale(input_np)
    input_buffer = PixelBuffer(grayscale_np)
else:
    st.info("Загрузите изображение в боковой панели")
    st.stop()

st.sidebar.header("Алгоритмы обработки")

method = st.sidebar.radio(
    "Выберите алгоритм обработки",
    ("Нелиный фильтр", "Локальная пороговая обработка")
)

st.sidebar.header("Параметры")

if method == "Нелиный фильтр":
    filter_type = st.sidebar.selectbox(
        "Тип фильтра",
        (
            ("min", "Фильтр минимума"),
            ("max", "Фильтр максимума"),
            ("median", "Медианный фильтр")
        ),
        format_func=lambda x: x[1]
    )[0]

    color_mode = edge_processing = st.sidebar.radio(
        "Цветовой режим",
        ("Полутоновое", "Цветное")
    )

    
    filter_radius = st.sidebar.slider(
        "Радиус фильтра",
        min_value=1,
        max_value=10,
        value=1,
        step=1
    )

    edge_processing = st.sidebar.radio(
        "Алгоритм обработки краев",
        ("Clamp", "Reflect")
    )

    if color_mode == "Полутоновое":
        output_buffer = apply_filter(
            buffer=input_buffer,
            radius=filter_radius,
            process_function=filter_type,
            padding_method=edge_processing
        )
    else:
        output_buffer = apply_filter(
            buffer=input_rgb_buffer,
            radius=filter_radius,
            process_function=filter_type,
            padding_method=edge_processing,
            rgb_channels=True
        )
else:
    thresholding_algorithm = st.sidebar.selectbox(
        "Методы локальной пороговой обработки",
        ("Метод Ниблэка", "Метод Сауволы")
    )

    window_radius = st.sidebar.slider(
        "Радиус окна",
        min_value=1,
        max_value=50,
        value=15,
        step=1
    )

    if thresholding_algorithm == "Метод Сауволы":
        k = 0.5
        min_k = 0.2
        max_k = 0.5
    else:
        k = -0.2
        min_k = -1.0
        max_k = 1.0

    k_val = st.sidebar.slider(
        "Коэффициент (k)",
        min_value=min_k,
        max_value=max_k,
        value=k,
        step=0.05
    )

    edge_processing = st.sidebar.radio(
        "Алгоритм обработки краев",
        ("Clamp", "Reflect")
    )

    if thresholding_algorithm == "Метод Ниблэка":
        output_buffer = apply_niblak_thresholding(
            buffer=input_buffer,
            radius=window_radius,
            k=k_val,
            padding_method=edge_processing
        )
    else:
        output_buffer = apply_sauvola_thresholding(
            buffer=input_buffer,
            radius=window_radius,
            k=k_val,
            padding_method=edge_processing
        )

if output_buffer is not None:
    c1, c2 = st.columns(2)
    with c1:
        st.header("До обработки")
        st.image(input_np)
    with c2:
        st.header("После обработки")
        st.image(output_buffer.data)
else:
    st.header("In developing")