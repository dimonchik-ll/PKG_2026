import streamlit as st

from color_math import (
    rgb_to_hsv,
    hsv_to_rgb,
    rgb_to_lab,
    lab_to_rgb,
    hsv_to_lab,
    lab_to_hsv,
)


st.set_page_config(page_title="Color Converter", layout="wide")


st.markdown(
    """
    <style>
    div[data-testid="stColorPicker"] button {
        width: 220px;
        height: 120px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)



def to_hex(r, g, b):
    r = round(max(0, min(255, r)))
    g = round(max(0, min(255, g)))
    b = round(max(0, min(255, b)))
    return f"#{r:02x}{g:02x}{b:02x}"


def hex_to_rgb(value):
    value = value.lstrip("#")
    return (
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
    )



def show_color(color, title):
    st.markdown(
        f"""
        <div style="
            width: 220px;
            height: 120px;
            background-color: {color};
            border: 1px solid black;
            border-radius: 10px;
        "></div>
        """,
        unsafe_allow_html=True
    )
    st.caption(title)


def sync_widgets(skip=None):
    values = {
        "r_slider": round(st.session_state.r),
        "g_slider": round(st.session_state.g),
        "b_slider": round(st.session_state.b),
        "r_number": round(st.session_state.r),
        "g_number": round(st.session_state.g),
        "b_number": round(st.session_state.b),

        "h_slider": float(st.session_state.h),
        "s_slider": float(st.session_state.s),
        "v_slider": float(st.session_state.v),
        "h_number": float(st.session_state.h),
        "s_number": float(st.session_state.s),
        "v_number": float(st.session_state.v),

        "l_slider": float(st.session_state.l),
        "a_slider": float(st.session_state.a),
        "lab_b_slider": float(st.session_state.lab_b),
        "l_number": float(st.session_state.l),
        "a_number": float(st.session_state.a),
        "lab_b_number": float(st.session_state.lab_b),
    }

    color = to_hex(
        st.session_state.r,
        st.session_state.g,
        st.session_state.b,
    )

    values["rgb_picker"] = color
    values["hsv_picker"] = color
    values["lab_picker"] = color

    for key, value in values.items():
        if key != skip:
            st.session_state[key] = value


def update_from_rgb(source_key, component):
    setattr(st.session_state, component, st.session_state[source_key])

    h, s, v = rgb_to_hsv(
        st.session_state.r,
        st.session_state.g,
        st.session_state.b,
    )

    l, a, lab_b = rgb_to_lab(
        st.session_state.r,
        st.session_state.g,
        st.session_state.b,
    )

    st.session_state.h = h
    st.session_state.s = s
    st.session_state.v = v

    st.session_state.l = l
    st.session_state.a = a
    st.session_state.lab_b = lab_b

    st.session_state.clipped = False
    sync_widgets(source_key)


def update_from_hsv(source_key, component):
    setattr(st.session_state, component, st.session_state[source_key])

    r, g, b = hsv_to_rgb(
        st.session_state.h,
        st.session_state.s,
        st.session_state.v,
    )

    l, a, lab_b = hsv_to_lab(
        st.session_state.h,
        st.session_state.s,
        st.session_state.v,
    )

    st.session_state.r = r
    st.session_state.g = g
    st.session_state.b = b

    st.session_state.l = l
    st.session_state.a = a
    st.session_state.lab_b = lab_b

    st.session_state.clipped = False
    sync_widgets(source_key)


def update_from_lab(source_key, component):
    setattr(st.session_state, component, st.session_state[source_key])

    r, g, b, clipped_rgb = lab_to_rgb(
        st.session_state.l,
        st.session_state.a,
        st.session_state.lab_b,
    )

    h, s, v, clipped_hsv = lab_to_hsv(
        st.session_state.l,
        st.session_state.a,
        st.session_state.lab_b,
    )

    st.session_state.r = r
    st.session_state.g = g
    st.session_state.b = b

    st.session_state.h = h
    st.session_state.s = s
    st.session_state.v = v

    st.session_state.clipped = clipped_rgb or clipped_hsv
    sync_widgets(source_key)


def update_from_picker(source_key):
    r, g, b = hex_to_rgb(st.session_state[source_key])

    st.session_state.r = r
    st.session_state.g = g
    st.session_state.b = b

    h, s, v = rgb_to_hsv(r, g, b)
    l, a, lab_b = rgb_to_lab(r, g, b)

    st.session_state.h = h
    st.session_state.s = s
    st.session_state.v = v

    st.session_state.l = l
    st.session_state.a = a
    st.session_state.lab_b = lab_b

    st.session_state.clipped = False
    sync_widgets(source_key)


if "initialized" not in st.session_state:
    st.session_state.r = 255
    st.session_state.g = 0
    st.session_state.b = 0

    h, s, v = rgb_to_hsv(255, 0, 0)
    l, a, lab_b = rgb_to_lab(255, 0, 0)

    st.session_state.h = h
    st.session_state.s = s
    st.session_state.v = v

    st.session_state.l = l
    st.session_state.a = a
    st.session_state.lab_b = lab_b

    st.session_state.clipped = False
    st.session_state.initialized = True

    sync_widgets()


st.title("Color Converter")

rgb_col, hsv_col, lab_col = st.columns(3)


with rgb_col:
    st.subheader("RGB")

    st.slider(
        "R",
        min_value=0,
        max_value=255,
        key="r_slider",
        on_change=update_from_rgb,
        args=("r_slider", "r"),
    )
    st.number_input(
        "R",
        min_value=0,
        max_value=255,
        step=1,
        key="r_number",
        on_change=update_from_rgb,
        args=("r_number", "r"),
    )

    st.slider(
        "G",
        min_value=0,
        max_value=255,
        key="g_slider",
        on_change=update_from_rgb,
        args=("g_slider", "g"),
    )
    st.number_input(
        "G",
        min_value=0,
        max_value=255,
        step=1,
        key="g_number",
        on_change=update_from_rgb,
        args=("g_number", "g"),
    )

    st.slider(
        "B",
        min_value=0,
        max_value=255,
        key="b_slider",
        on_change=update_from_rgb,
        args=("b_slider", "b"),
    )
    st.number_input(
        "B",
        min_value=0,
        max_value=255,
        step=1,
        key="b_number",
        on_change=update_from_rgb,
        args=("b_number", "b"),
    )

    st.color_picker(
        "RGB palette",
        key="rgb_picker",
        on_change=update_from_picker,
        args=("rgb_picker",),
    )

    show_color(st.session_state.rgb_picker, "RGB result")


with hsv_col:
    st.subheader("HSV")

    st.slider(
        "H",
        min_value=0.0,
        max_value=360.0,
        step=0.1,
        key="h_slider",
        on_change=update_from_hsv,
        args=("h_slider", "h"),
    )
    st.number_input(
        "H",
        min_value=0.0,
        max_value=360.0,
        step=0.1,
        key="h_number",
        on_change=update_from_hsv,
        args=("h_number", "h"),
    )

    st.slider(
        "S",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        key="s_slider",
        on_change=update_from_hsv,
        args=("s_slider", "s"),
    )
    st.number_input(
        "S",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        key="s_number",
        on_change=update_from_hsv,
        args=("s_number", "s"),
    )

    st.slider(
        "V",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        key="v_slider",
        on_change=update_from_hsv,
        args=("v_slider", "v"),
    )
    st.number_input(
        "V",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        key="v_number",
        on_change=update_from_hsv,
        args=("v_number", "v"),
    )

    st.color_picker(
        "HSV palette",
        key="hsv_picker",
        on_change=update_from_picker,
        args=("hsv_picker",),
    )

    show_color(st.session_state.hsv_picker, "HSV result")


with lab_col:
    st.subheader("LAB")

    st.slider(
        "L",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        key="l_slider",
        on_change=update_from_lab,
        args=("l_slider", "l"),
    )
    st.number_input(
        "L",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        key="l_number",
        on_change=update_from_lab,
        args=("l_number", "l"),
    )

    st.slider(
        "a",
        min_value=-128.0,
        max_value=127.0,
        step=0.1,
        key="a_slider",
        on_change=update_from_lab,
        args=("a_slider", "a"),
    )
    st.number_input(
        "a",
        min_value=-128.0,
        max_value=127.0,
        step=0.1,
        key="a_number",
        on_change=update_from_lab,
        args=("a_number", "a"),
    )

    st.slider(
        "b",
        min_value=-128.0,
        max_value=127.0,
        step=0.1,
        key="lab_b_slider",
        on_change=update_from_lab,
        args=("lab_b_slider", "lab_b"),
    )
    st.number_input(
        "b",
        min_value=-128.0,
        max_value=127.0,
        step=0.1,
        key="lab_b_number",
        on_change=update_from_lab,
        args=("lab_b_number", "lab_b"),
    )

    st.color_picker(
        "LAB palette",
        key="lab_picker",
        on_change=update_from_picker,
        args=("lab_picker",),
    )

    show_color(st.session_state.lab_picker, "LAB result")


if st.session_state.clipped:
    st.warning(
        "Цвет LAB выходит за пределы sRGB. "
        "Для отображения значения RGB были ограничены допустимым диапазоном."
    )
