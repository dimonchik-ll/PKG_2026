import os
import math
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw

try:
    from numba import njit
except ImportError:
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class PixelBuffer:
    def __init__(self, width: int, height: int, channels: int = 1, raw_bytes: bytearray = None):
        self.width = width
        self.height = height
        self.channels = channels
        size = width * height * channels
        if raw_bytes is not None:
            if len(raw_bytes) != size:
                raise ValueError("Размер буфера не совпадает с размерностью изображения.")
            self.data = bytearray(raw_bytes)
        else:
            self.data = bytearray(size)
        self.view = memoryview(self.data)

    @classmethod
    def from_numpy(cls, arr: np.ndarray) -> 'PixelBuffer':
        arr = np.ascontiguousarray(arr, dtype=np.uint8)
        if arr.ndim == 2:
            h, w = arr.shape
            c = 1
        else:
            h, w, c = arr.shape
        return cls(w, h, c, bytearray(arr.tobytes()))

    def to_numpy(self) -> np.ndarray:
        arr = np.frombuffer(self.data, dtype=np.uint8).copy()
        if self.channels == 1:
            return arr.reshape((self.height, self.width))
        return arr.reshape((self.height, self.width, self.channels))

    @staticmethod
    def resolve_coord(coord: int, max_val: int, mode: str) -> int:
        if 0 <= coord < max_val:
            return coord
        if mode == "clamp":
            return 0 if coord < 0 else max_val - 1
        elif mode == "reflect":
            if max_val <= 1:
                return 0
            while coord < 0 or coord >= max_val:
                if coord < 0:
                    coord = -coord - 1
                if coord >= max_val:
                    coord = 2 * max_val - coord - 1
            return coord
        raise ValueError(f"Неизвестный режим обработки краев: {mode}")

    def get_pixel(self, x: int, y: int, c: int = 0, edge_mode: str = "clamp") -> int:
        rx = self.resolve_coord(x, self.width, edge_mode)
        ry = self.resolve_coord(y, self.height, edge_mode)
        idx = (ry * self.width + rx) * self.channels + c
        return self.view[idx]

    def set_pixel(self, x: int, y: int, val: int, c: int = 0) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            idx = (y * self.width + x) * self.channels + c
            self.view[idx] = max(0, min(255, int(val)))

    def create_padded_array(self, radius: int, edge_mode: str = "clamp") -> np.ndarray:
        src = self.to_numpy()
        pad_h = self.height + 2 * radius
        pad_w = self.width + 2 * radius

        if self.channels == 1:
            padded = np.empty((pad_h, pad_w), dtype=np.uint8)
        else:
            padded = np.empty((pad_h, pad_w, self.channels), dtype=np.uint8)

        y_map = [self.resolve_coord(y - radius, self.height, edge_mode) for y in range(pad_h)]
        x_map = [self.resolve_coord(x - radius, self.width, edge_mode) for x in range(pad_w)]

        for py, sy in enumerate(y_map):
            for px, sx in enumerate(x_map):
                padded[py, px] = src[sy, sx]

        return padded


@njit
def _insertion_sort(arr: np.ndarray, length: int):
    for i in range(1, length):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


@njit
def _process_order_statistic(
    padded: np.ndarray,
    out: np.ndarray,
    height: int,
    width: int,
    radius: int,
    stat_type_id: int,
    percentile: float,
    alpha_trim: int
):
    k_size = 2 * radius + 1
    win_len = k_size * k_size
    window = np.empty(win_len, dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            idx = 0
            for ky in range(k_size):
                for kx in range(k_size):
                    window[idx] = padded[y + ky, x + kx]
                    idx += 1

            _insertion_sort(window, win_len)

            if stat_type_id == 0:
                out[y, x] = window[win_len // 2]
            elif stat_type_id == 1:
                out[y, x] = window[0]
            elif stat_type_id == 2:
                out[y, x] = window[win_len - 1]
            elif stat_type_id == 3:
                out[y, x] = (int(window[0]) + int(window[win_len - 1])) // 2
            elif stat_type_id == 4:
                p_idx = int(round((percentile / 100.0) * (win_len - 1)))
                p_idx = max(0, min(win_len - 1, p_idx))
                out[y, x] = window[p_idx]
            elif stat_type_id == 5:
                trim = alpha_trim
                if 2 * trim >= win_len:
                    trim = (win_len - 1) // 2
                s = 0
                count = win_len - 2 * trim
                for i in range(trim, win_len - trim):
                    s += int(window[i])
                out[y, x] = s // count


def apply_order_statistic_filter(
    buffer: PixelBuffer,
    radius: int = 1,
    stat_type: str = "median",
    edge_mode: str = "reflect",
    percentile: float = 50.0,
    alpha_trim: int = 2
) -> PixelBuffer:
    stat_map = {
        "median": 0,
        "min": 1,
        "max": 2,
        "midpoint": 3,
        "percentile": 4,
        "alpha_trimmed": 5
    }
    stat_id = stat_map.get(stat_type, 0)

    padded = buffer.create_padded_array(radius, edge_mode=edge_mode)
    h, w, c = buffer.height, buffer.width, buffer.channels

    if c == 1:
        out = np.empty((h, w), dtype=np.uint8)
        _process_order_statistic(padded, out, h, w, radius, stat_id, percentile, alpha_trim)
    else:
        out = np.empty((h, w, c), dtype=np.uint8)
        for ch_idx in range(c):
            ch_in = np.ascontiguousarray(padded[:, :, ch_idx])
            ch_out = np.empty((h, w), dtype=np.uint8)
            _process_order_statistic(ch_in, ch_out, h, w, radius, stat_id, percentile, alpha_trim)
            out[:, :, ch_idx] = ch_out

    return PixelBuffer.from_numpy(out)


@njit
def compute_integral_images(img_gray: np.ndarray):
    h, w = img_gray.shape
    sat = np.zeros((h + 1, w + 1), dtype=np.int64)
    sat_sq = np.zeros((h + 1, w + 1), dtype=np.int64)

    for y in range(1, h + 1):
        row_sum = 0
        row_sq_sum = 0
        for x in range(1, w + 1):
            val = int(img_gray[y - 1, x - 1])
            row_sum += val
            row_sq_sum += val * val
            sat[y, x] = sat[y - 1, x] + row_sum
            sat_sq[y, x] = sat_sq[y - 1, x] + row_sq_sum

    return sat, sat_sq


@njit
def _get_window_stats_sat(sat: np.ndarray, sat_sq: np.ndarray, x0: int, y0: int, x1: int, y1: int):
    area = (x1 - x0 + 1) * (y1 - y0 + 1)
    s1 = sat[y1 + 1, x1 + 1] - sat[y0, x1 + 1] - sat[y1 + 1, x0] + sat[y0, x0]
    s2 = sat_sq[y1 + 1, x1 + 1] - sat_sq[y0, x1 + 1] - sat_sq[y1 + 1, x0] + sat_sq[y0, x0]

    mean = s1 / area
    variance = (s2 / area) - (mean * mean)
    if variance < 0.0:
        variance = 0.0
    return mean, math.sqrt(variance)


@njit
def _threshold_sat(
    img_gray: np.ndarray,
    sat: np.ndarray,
    sat_sq: np.ndarray,
    out: np.ndarray,
    window_size: int,
    method_id: int,
    k_param: float,
    r_param: float,
    c_offset: float
):
    h, w = img_gray.shape
    half = window_size // 2

    min_gray = 0.0
    if method_id == 2:
        min_val = 255
        for ry in range(h):
            for rx in range(w):
                if img_gray[ry, rx] < min_val:
                    min_val = img_gray[ry, rx]
        min_gray = float(min_val)

    for y in range(h):
        y0 = max(0, y - half)
        y1 = min(h - 1, y + half)
        for x in range(w):
            x0 = max(0, x - half)
            x1 = min(w - 1, x + half)

            mean, std = _get_window_stats_sat(sat, sat_sq, x0, y0, x1, y1)

            if method_id == 0:
                thresh = mean + k_param * std
            elif method_id == 1:
                thresh = mean * (1.0 + k_param * ((std / r_param) - 1.0))
            elif method_id == 2:
                r_max = max(r_param, std, 1e-5)
                thresh = (1.0 - k_param) * mean + k_param * min_gray + k_param * (std / r_max) * (mean - min_gray)
            elif method_id == 3:
                thresh = mean - c_offset
            else:
                thresh = mean * (1.0 - (c_offset / 100.0))

            out[y, x] = 255 if img_gray[y, x] > thresh else 0


@njit
def _rgb_to_gray_loop(src: np.ndarray) -> np.ndarray:
    h, w, _ = src.shape
    gray = np.empty((h, w), dtype=np.uint8)
    for y in range(h):
        for x in range(w):
            r = int(src[y, x, 0])
            g = int(src[y, x, 1])
            b = int(src[y, x, 2])
            gray[y, x] = (77 * r + 150 * g + 29 * b) >> 8
    return gray


def rgb_to_grayscale_manual(buffer: PixelBuffer) -> PixelBuffer:
    if buffer.channels == 1:
        return buffer
    gray = _rgb_to_gray_loop(buffer.to_numpy())
    return PixelBuffer.from_numpy(gray)


def apply_local_or_adaptive_threshold(
    buffer: PixelBuffer,
    method: str = "sauvola",
    window_size: int = 15,
    k_param: float = 0.2,
    r_param: float = 128.0,
    c_offset: float = 10.0
) -> PixelBuffer:
    gray_buf = rgb_to_grayscale_manual(buffer)
    img_gray = gray_buf.to_numpy()
    h, w = img_gray.shape
    out = np.empty((h, w), dtype=np.uint8)

    sat, sat_sq = compute_integral_images(img_gray)

    method_map = {
        "niblack": 0,
        "sauvola": 1,
        "wolf": 2,
        "adaptive_mean": 3,
        "adaptive_bradley": 4
    }
    m_id = method_map.get(method, 1)

    _threshold_sat(img_gray, sat, sat_sq, out, window_size, m_id, k_param, r_param, c_offset)

    return PixelBuffer.from_numpy(out)


def generate_test_suite(output_dir: str = "test_images"):
    os.makedirs(output_dir, exist_ok=True)
    expected = [
        "1_noisy_salt_pepper.png",
        "2_sauvola_beats_niblack.png",
        "3_niblack_beats_sauvola_faint.png",
        "4_adaptive_extreme_shadow.png"
    ]
    if all(os.path.exists(os.path.join(output_dir, f)) for f in expected):
        return

    w, h = 512, 384
    rng = np.random.default_rng(42)

    img1 = Image.new("L", (w, h), 200)
    draw1 = ImageDraw.Draw(img1)
    draw1.rectangle([40, 40, 220, 180], fill=60, outline=20, width=3)
    draw1.ellipse([260, 50, 460, 220], fill=110, outline=30, width=3)
    draw1.polygon([(80, 340), (250, 220), (420, 340)], fill=40)
    draw1.text((130, 345), "ORDER STATISTICS TEST (SALT & PEPPER)", fill=15)
    arr1 = np.array(img1, dtype=np.uint8)
    noise_mask = rng.random((h, w))
    arr1[noise_mask < 0.06] = 0
    arr1[noise_mask > 0.94] = 255
    Image.fromarray(arr1).save(os.path.join(output_dir, "1_noisy_salt_pepper.png"))

    img2 = Image.new("L", (w, h), 235)
    draw2 = ImageDraw.Draw(img2)
    draw2.rectangle([25, 25, w - 25, h - 25], outline=80, width=2)
    lines = [
        "SAUVOLA VS NIBLACK COMPARISON",
        "--------------------------------------------",
        "Sauvola suppresses background noise in",
        "uniform light regions using standard",
        "deviation normalization (s / R - 1).",
        "",
        "Niblack (T = m + k*s) amplifies tiny",
        "sensor fluctuations on empty white background,",
        "creating false black salt-like artifacts.",
        "",
        "Formula: T = m * [1 + k * (s/R - 1)]"
    ]
    y_pos = 50
    for line in lines:
        draw2.text((45, y_pos), line, fill=35)
        y_pos += 26
    arr2 = np.array(img2, dtype=np.int16)
    xx, yy = np.meshgrid(np.linspace(0, 1, w), np.linspace(0, 1, h))
    vignette = (-35 * (xx**2 + yy**2)).astype(np.int16)
    sensor_noise = rng.normal(0, 4.5, (h, w)).astype(np.int16)
    arr2 = np.clip(arr2 + vignette + sensor_noise, 0, 255).astype(np.uint8)
    Image.fromarray(arr2).save(os.path.join(output_dir, "2_sauvola_beats_niblack.png"))

    img3 = Image.new("L", (w, h), 180)
    draw3 = ImageDraw.Draw(img3)
    draw3.text((40, 30), "LOW-CONTRAST FAINT LINES (NIBLACK WINS)", fill=158)
    for r in range(30, 140, 18):
        draw3.ellipse([w // 2 - r, h // 2 - r + 15, w // 2 + r, h // 2 + r + 15], outline=162, width=2)
    for x_line in range(60, w - 60, 25):
        draw3.line([(x_line, 80), (x_line, h - 40)], fill=165, width=1)
    arr3 = np.array(img3, dtype=np.int16)
    arr3 = np.clip(arr3 + rng.normal(0, 1.5, (h, w)), 0, 255).astype(np.uint8)
    Image.fromarray(arr3).save(os.path.join(output_dir, "3_niblack_beats_sauvola_faint.png"))

    img4 = Image.new("L", (w, h), 255)
    draw4 = ImageDraw.Draw(img4)
    for idx, y_pos in enumerate(range(35, h - 35, 32)):
        draw4.text((35, y_pos), f"Row {idx+1}: Adaptive Thresholding handles harsh shadows & spotlights!", fill=60)
        draw4.rectangle([390, y_pos, 480, y_pos + 18], fill=50)
    arr4 = np.array(img4, dtype=np.float32)
    illum = 0.20 + 0.80 * (0.6 * xx + 0.4 * (1.0 - yy)) + 0.35 * np.exp(-((xx - 0.25)**2 + (yy - 0.75)**2) / 0.04)
    illum = np.clip(illum, 0.15, 1.15)
    arr4 = np.clip(arr4 * illum, 0, 255).astype(np.uint8)
    Image.fromarray(arr4).save(os.path.join(output_dir, "4_adaptive_extreme_shadow.png"))


def main():
    st.set_page_config(page_title="ЛР №3 — Вариант 15", layout="wide")

    test_dir = "test_images"
    generate_test_suite(test_dir)

    st.title("Лабораторная работа №3 — Вариант 15")

    st.sidebar.header("1. Источник изображения")
    source_mode = st.sidebar.radio(
        "Выберите источник:",
        ["Встроенная база тестовых картинок", "Загрузить свой файл"]
    )

    loaded_pil = None
    if source_mode == "Встроенная база тестовых картинок":
        test_names = {
            "1_noisy_salt_pepper.png": "1. Шум «Соль и перец»",
            "2_sauvola_beats_niblack.png": "2. Документ с шумом фона",
            "3_niblack_beats_sauvola_faint.png": "3. Малоконтрастные линии",
            "4_adaptive_extreme_shadow.png": "4. Резкая тень и блик"
        }
        choice = st.sidebar.selectbox(
            "Тестовое изображение:",
            options=list(test_names.keys()),
            format_func=lambda k: test_names.get(k, k)
        )
        loaded_pil = Image.open(os.path.join(test_dir, choice))
    else:
        uploaded = st.sidebar.file_uploader("Загрузите изображение (PNG, JPG, BMP)", type=["png", "jpg", "jpeg", "bmp"])
        if uploaded is not None:
            loaded_pil = Image.open(uploaded)

    st.sidebar.header("2. Режим и алгоритм")
    color_mode = st.sidebar.selectbox("Цветовой режим:", ["Полутоновое (Grayscale)", "Цветное (RGB)"])

    algo_category = st.sidebar.radio(
        "Группа методов:",
        [
            "1. Нелинейные фильтры (порядковые статистики)",
            "2. Локальная пороговая обработка",
            "3. Адаптивная пороговая обработка"
        ]
    )

    if loaded_pil is None:
        st.info("Загрузите изображение в боковой панели.")
        st.stop()

    if color_mode.startswith("Полутоновое") or not algo_category.startswith("1."):
        working_pil = loaded_pil.convert("L")
    else:
        working_pil = loaded_pil.convert("RGB")

    input_np = np.array(working_pil, dtype=np.uint8)
    input_buffer = PixelBuffer.from_numpy(input_np)

    st.sidebar.subheader("Параметры метода")
    local_mode = None

    if algo_category == "1. Нелинейные фильтры (порядковые статистики)":
        stat_label = st.sidebar.selectbox(
            "Тип порядковой статистики:",
            [
                ("median", "Медианный фильтр (Median)"),
                ("min", "Минимум (Min)"),
                ("max", "Максимум (Max)"),
                ("midpoint", "Срединная точка (Midpoint)"),
                ("alpha_trimmed", "Альфа-усеченное среднее (Alpha-trimmed)"),
                ("percentile", "Произвольный перцентиль (Percentile)")
            ],
            format_func=lambda x: x[1]
        )[0]

        radius = st.sidebar.slider("Радиус фильтра (R):", min_value=1, max_value=7, value=1)
        edge_mode = st.sidebar.radio(
            "Обработка краев:",
            [("reflect", "Зеркальное отражение (Reflect)"), ("clamp", "Дублирование пикселей (Clamp)")],
            format_func=lambda x: x[1]
        )[0]

        percentile_val = 50.0
        alpha_trim_val = 2
        if stat_label == "percentile":
            percentile_val = float(st.sidebar.slider("Перцентиль (%):", 0, 100, 50))
        elif stat_label == "alpha_trimmed":
            max_trim = ((2 * radius + 1) ** 2 - 1) // 2
            alpha_trim_val = st.sidebar.slider("Отсекаемых элементов с края:", 1, max(1, max_trim), min(2, max(1, max_trim)))

        output_buffer = apply_order_statistic_filter(
            input_buffer,
            radius=radius,
            stat_type=stat_label,
            edge_mode=edge_mode,
            percentile=percentile_val,
            alpha_trim=alpha_trim_val
        )

    elif algo_category == "2. Локальная пороговая обработка":
        local_mode = st.sidebar.selectbox(
            "Метод локальной бинаризации:",
            [
                ("sauvola", "Метод Сауволы (Sauvola)"),
                ("niblack", "Метод Ниблэка (Niblack)"),
                ("wolf", "Метод Вульфа (Wolf)"),
                ("compare", "Сравнить Ниблэка и Сауволу")
            ],
            format_func=lambda x: x[1]
        )[0]

        win_size = st.sidebar.slider("Размер окна (W):", min_value=3, max_value=101, value=25, step=2)
        default_k = 0.2 if local_mode != "niblack" else -0.2
        k_val = st.sidebar.slider("Коэффициент (k):", min_value=-1.0, max_value=1.0, value=default_k, step=0.05)
        r_val = float(st.sidebar.slider("Динамический диапазон (R):", min_value=16, max_value=256, value=128))

        if local_mode == "compare":
            out_sauvola = apply_local_or_adaptive_threshold(
                input_buffer, method="sauvola", window_size=win_size, k_param=abs(k_val), r_param=r_val
            )
            out_niblack = apply_local_or_adaptive_threshold(
                input_buffer, method="niblack", window_size=win_size, k_param=-abs(k_val), r_param=r_val
            )
            output_buffer = out_sauvola
        else:
            output_buffer = apply_local_or_adaptive_threshold(
                input_buffer,
                method=local_mode,
                window_size=win_size,
                k_param=k_val,
                r_param=r_val
            )

    else:
        adapt_mode = st.sidebar.selectbox(
            "Алгоритм адаптивного порога:",
            [
                ("adaptive_mean", "Локальное среднее с поправкой C (T = m - C)"),
                ("adaptive_bradley", "Метод Брэдли-Рота (T = m * (1 - t/100))")
            ],
            format_func=lambda x: x[1]
        )[0]

        win_size = st.sidebar.slider("Размер окна (W):", min_value=3, max_value=151, value=35, step=2)
        c_val = float(st.sidebar.slider("Поправка C / процент t:", min_value=-30, max_value=50, value=12))

        output_buffer = apply_local_or_adaptive_threshold(
            input_buffer,
            method=adapt_mode,
            window_size=win_size,
            c_offset=c_val
        )

    if algo_category.startswith("2.") and local_mode == "compare":
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("До обработки")
            st.image(input_buffer.to_numpy(), use_container_width=True, clamp=True)
        with c2:
            st.subheader("Метод Ниблэка")
            st.image(out_niblack.to_numpy(), use_container_width=True, clamp=True)
        with c3:
            st.subheader("Метод Сауволы")
            st.image(out_sauvola.to_numpy(), use_container_width=True, clamp=True)
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("До обработки")
            st.image(input_buffer.to_numpy(), use_container_width=True, clamp=True)
        with c2:
            st.subheader("После обработки")
            st.image(output_buffer.to_numpy(), use_container_width=True, clamp=True)


if __name__ == "__main__":
    main()