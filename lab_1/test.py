import streamlit as st

st.title("Color Picker")

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    r = st.slider("Red (R)", min_value=0, max_value=255, value=120)
    g = st.slider("Green (G)", min_value=0, max_value=255, value=180)
    b = st.slider("Blue (B)", min_value=0, max_value=255, value=220)

with col2:
    h = st.slider("Hue (H)", min_value=0, max_value=255, value=120)
    s = st.slider("Saturated (S)", min_value=0, max_value=255, value=180)
    v = st.slider("Value (V)", min_value=0, max_value=255, value=220)

with col3:
    l = st.slider("Lightness (L)", min_value=0, max_value=255, value=120)
    a = st.slider("Green-Red Axis (A)", min_value=0, max_value=255, value=180)
    b = st.slider("Blue-Yellow Axis) (B)", min_value=0, max_value=255, value=220)

with col4:
    st.subheader("Preview")
    square_html = f"""
    <div style="
        width: 180px;
        height: 180px;
        background-color: rgb({r}, {g}, {b});
        border: 2px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    "></div>
    """
    st.markdown(square_html, unsafe_allow_html=True)