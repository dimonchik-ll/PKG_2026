from pathlib import Path

import streamlit as st
from PIL import Image


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".gif",
    ".tif",
    ".tiff",
    ".bmp",
    ".png",
    ".pcx",
}


def get_color_depth(image):
    depths = {
        "1": 1,
        "L": 8,
        "P": 8,
        "RGB": 24,
        "RGBA": 32,
        "CMYK": 32,
        "LA": 16,
        "I;16": 16,
        "I": 32,
        "F": 32,
    }
    return depths.get(image.mode, "—")


def get_dpi(image):
    dpi = image.info.get("dpi")

    if isinstance(dpi, tuple) and len(dpi) >= 2:
        x = float(dpi[0])
        y = float(dpi[1])

        if x <= 0 or y <= 0:
            return "72.0", "72.0"

        return round(x, 2), round(y, 2)

    return "72.0", "72.0"


def get_compression(image):
    if image.format == "JPEG":
        return "JPEG"

    if image.format == "PNG":
        return "DEFLATE"

    if image.format == "GIF":
        return "LZW"

    if image.format == "PCX":
        return "RLE"

    if image.format == "BMP":
        compression = image.info.get("compression")
        if compression is None:
            return "Без сжатия"
        return str(compression)

    if image.format == "TIFF":
        compression = image.info.get("compression")
        if compression is not None:
            return str(compression)

        try:
            value = image.tag_v2.get(259)
            names = {
                1: "Без сжатия",
                2: "CCITT 1D",
                3: "Group 3 Fax",
                4: "Group 4 Fax",
                5: "LZW",
                6: "JPEG",
                7: "JPEG",
                8: "Deflate",
                32773: "PackBits",
                32946: "Deflate",
            }
            return names.get(value, str(value)) if value is not None else "—"
        except Exception:
            return "—"

    return "—"


def build_row(filename, image):
    width, height = image.size
    dpi_x, dpi_y = get_dpi(image)

    return {
        "Имя файла": filename,
        "Размер изображения": f"{width} × {height}",
        "Разрешение": (
            f"{dpi_x} × {dpi_y} dpi"
            if dpi_x != "—" and dpi_y != "—"
            else "—"
        ),
        "Глубина цвета": get_color_depth(image),
        "Сжатие": get_compression(image),
    }


def error_row(filename):
    return {
        "Имя файла": filename,
        "Размер изображения": "Ошибка",
        "Разрешение": "Ошибка",
        "Глубина цвета": "Ошибка",
        "Сжатие": "Ошибка",
    }


def read_uploaded_file(uploaded_file):
    uploaded_file.seek(0)

    with Image.open(uploaded_file) as image:
        return build_row(uploaded_file.name, image)


def read_file_from_folder(path):
    with Image.open(path) as image:
        return build_row(path.name, image)


st.title("Лабораторная работа №2")

source = st.radio(
    "Источник",
    ["Загрузить файлы", "Считать папку"],
    horizontal=True,
)

rows = []

if source == "Загрузить файлы":
    uploaded_files = st.file_uploader(
        "Загрузите изображения",
        type=["jpg", "jpeg", "gif", "tif", "tiff", "bmp", "png", "pcx"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                rows.append(read_uploaded_file(uploaded_file))
            except Exception:
                rows.append(error_row(uploaded_file.name))

else:
    folder_path = st.text_input("Путь к папке")

    if folder_path:
        folder = Path(folder_path)

        if not folder.exists() or not folder.is_dir():
            st.error("Папка не найдена")
        else:
            files = sorted(
                path
                for path in folder.iterdir()
                if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
            )

            for path in files:
                try:
                    rows.append(read_file_from_folder(path))
                except Exception:
                    rows.append(error_row(path.name))

if rows:
    st.dataframe(rows, use_container_width=True, hide_index=True)