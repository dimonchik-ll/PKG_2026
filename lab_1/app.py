import streamlit as st

from color_math import (
    hsv_to_lab,
    hsv_to_rgb,
    lab_to_hsv,
    lab_to_rgb,
    rgb_to_hsv,
    rgb_to_lab,
)


def update_from_rgb():
    st.session_state.clipped = False

    r = st.session_state.r
    g = st.session_state.g
    b = st.session_state.b

    h, s, v = rgb_to_hsv(r, g, b)
    l, a, lab_b = rgb_to_lab(r, g, b)

    st.session_state.h = round(h, 1)
    st.session_state.s = round(s, 1)
    st.session_state.v = round(v, 1)
    st.session_state.l = round(l, 1)
    st.session_state.a = round(a, 1)
    st.session_state.lab_b = round(lab_b, 1)


def update_from_hsv():
    st.session_state.clipped = False

    h = st.session_state.h
    s = st.session_state.s
    v = st.session_state.v

    r, g, b = hsv_to_rgb(h, s, v)
    l, a, lab_b = hsv_to_lab(h, s, v)

    st.session_state.r = round(r)
    st.session_state.g = round(g)
    st.session_state.b = round(b)
    st.session_state.l = round(l, 1)
    st.session_state.a = round(a, 1)
    st.session_state.lab_b = round(lab_b, 1)


def update_from_lab():
    l = st.session_state.l
    a = st.session_state.a
    lab_b = st.session_state.lab_b

    r, g, b, clipped_rgb = lab_to_rgb(l, a, lab_b)
    h, s, v, clipped_hsv = lab_to_hsv(l, a, lab_b)

    st.session_state.r = round(r)
    st.session_state.g = round(g)
    st.session_state.b = round(b)
    st.session_state.h = round(h, 1)
    st.session_state.s = round(s, 1)
    st.session_state.v = round(v, 1)
    st.session_state.clipped = clipped_rgb or clipped_hsv


def show_color(css_color):
    st.markdown(
        f'<div style="width:100%;height:70px;border-radius:10px;'
        f'background:{css_color};border:1px solid #777;"></div>',
        unsafe_allow_html=True,
    )


def hsv_css_color(h, s, v):
    r, g, b = hsv_to_rgb(h, s, v)
    return f"rgb({round(r)} {round(g)} {round(b)})"


if "r" not in st.session_state:
    st.session_state.r = 255
    st.session_state.g = 255
    st.session_state.b = 255

    h, s, v = rgb_to_hsv(255, 255, 255)
    l, a, lab_b = rgb_to_lab(255, 255, 255)

    st.session_state.h = round(h, 1)
    st.session_state.s = round(s, 1)
    st.session_state.v = round(v, 1)
    st.session_state.l = round(l, 1)
    st.session_state.a = round(a, 1)
    st.session_state.lab_b = round(lab_b, 1)
    st.session_state.clipped = False


rgb_col, hsv_col, lab_col = st.columns(3)

with rgb_col:
    st.subheader("RGB")
    st.slider("R", 0, 255, key="r", on_change=update_from_rgb)
    st.slider("G", 0, 255, key="g", on_change=update_from_rgb)
    st.slider("B", 0, 255, key="b", on_change=update_from_rgb)
    st.write("Итоговый цвет RGB")
    show_color(f"rgb({st.session_state.r} {st.session_state.g} {st.session_state.b})")

with hsv_col:
    st.subheader("HSV")
    st.slider("H", 0.0, 360.0, step=1.0, key="h", on_change=update_from_hsv)
    st.slider("S", 0.0, 100.0, step=1.0, key="s", on_change=update_from_hsv)
    st.slider("V", 0.0, 100.0, step=1.0, key="v", on_change=update_from_hsv)
    st.write("Итоговый цвет HSV")
    show_color(hsv_css_color(st.session_state.h, st.session_state.s, st.session_state.v))

with lab_col:
    st.subheader("LAB")
    st.slider("L*", 0.0, 100.0, step=1.0, key="l", on_change=update_from_lab)
    st.slider("a*", -128.0, 127.0, step=1.0, key="a", on_change=update_from_lab)
    st.slider("b*", -128.0, 127.0, step=1.0, key="lab_b", on_change=update_from_lab)
    st.write("Итоговый цвет LAB")
    show_color(
        f"lab({st.session_state.l}% {st.session_state.a} {st.session_state.lab_b})"
    )

if st.session_state.get("clipped"):
    st.warning("Цвет LAB выходит за диапазон RGB, поэтому значения были обрезаны.")
