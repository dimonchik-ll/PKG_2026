X_WHITE = 95.047
Y_WHITE = 100.0
Z_WHITE = 108.883


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def to_linear(value):
    if value >= 0.04045:
        return ((value + 0.055) / 1.055) ** 2.4
    return value / 12.92


def from_linear(value):
    if value >= 0.0031308:
        return 1.055 * value ** (1 / 2.4) - 0.055
    return 12.92 * value


def lab_f(value):
    if value >= 0.008856:
        return value ** (1 / 3)
    return 7.787 * value + 16 / 116


def lab_f_inverse(value):
    if value ** 3 >= 0.008856:
        return value ** 3
    return (value - 16 / 116) / 7.787


def rgb_to_hsv(r, g, b):
    r /= 255
    g /= 255
    b /= 255

    maximum = max(r, g, b)
    minimum = min(r, g, b)
    delta = maximum - minimum

    if delta == 0:
        h = 0
    elif maximum == r:
        h = 60 * (((g - b) / delta) % 6)
    elif maximum == g:
        h = 60 * (((b - r) / delta) + 2)
    else:
        h = 60 * (((r - g) / delta) + 4)

    s = 0 if maximum == 0 else delta / maximum
    v = maximum

    return h, s * 100, v * 100


def hsv_to_rgb(h, s, v):
    h %= 360
    s /= 100
    v /= 100

    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    return (r + m) * 255, (g + m) * 255, (b + m) * 255


def rgb_to_lab(r, g, b):
    r = to_linear(r / 255) * 100
    g = to_linear(g / 255) * 100
    b = to_linear(b / 255) * 100

    x = 0.412453 * r + 0.357580 * g + 0.180423 * b
    y = 0.212671 * r + 0.715160 * g + 0.072169 * b
    z = 0.019334 * r + 0.119193 * g + 0.950227 * b

    fx = lab_f(x / X_WHITE)
    fy = lab_f(y / Y_WHITE)
    fz = lab_f(z / Z_WHITE)

    l = 116 * fy - 16
    a = 500 * (fx - fy)
    lab_b = 200 * (fy - fz)

    return l, a, lab_b


def lab_to_rgb(l, a, lab_b):
    fy = (l + 16) / 116
    fx = fy + a / 500
    fz = fy - lab_b / 200

    x = X_WHITE * lab_f_inverse(fx) / 100
    y = Y_WHITE * lab_f_inverse(fy) / 100
    z = Z_WHITE * lab_f_inverse(fz) / 100

    r = 3.2406 * x - 1.5372 * y - 0.4986 * z
    g = -0.9689 * x + 1.8758 * y + 0.0415 * z
    b = 0.0557 * x - 0.2040 * y + 1.0570 * z

    r = from_linear(r) * 255
    g = from_linear(g) * 255
    b = from_linear(b) * 255

    clipped = r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255

    return clamp(r, 0, 255), clamp(g, 0, 255), clamp(b, 0, 255), clipped

def hsv_to_lab(h, s, v):
    h %= 360
    s /= 100
    v /= 100

    c = v * s
    x_color = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if h < 60:
        r, g, b = c, x_color, 0
    elif h < 120:
        r, g, b = x_color, c, 0
    elif h < 180:
        r, g, b = 0, c, x_color
    elif h < 240:
        r, g, b = 0, x_color, c
    elif h < 300:
        r, g, b = x_color, 0, c
    else:
        r, g, b = c, 0, x_color

    r = to_linear(r + m) * 100
    g = to_linear(g + m) * 100
    b = to_linear(b + m) * 100

    x = 0.412453 * r + 0.357580 * g + 0.180423 * b
    y = 0.212671 * r + 0.715160 * g + 0.072169 * b
    z = 0.019334 * r + 0.119193 * g + 0.950227 * b

    fx = lab_f(x / X_WHITE)
    fy = lab_f(y / Y_WHITE)
    fz = lab_f(z / Z_WHITE)

    l = 116 * fy - 16
    a = 500 * (fx - fy)
    lab_b = 200 * (fy - fz)

    return l, a, lab_b


def lab_to_hsv(l, a, lab_b):
    fy = (l + 16) / 116
    fx = fy + a / 500
    fz = fy - lab_b / 200

    x = X_WHITE * lab_f_inverse(fx) / 100
    y = Y_WHITE * lab_f_inverse(fy) / 100
    z = Z_WHITE * lab_f_inverse(fz) / 100

    r = from_linear(3.2406 * x - 1.5372 * y - 0.4986 * z)
    g = from_linear(-0.9689 * x + 1.8758 * y + 0.0415 * z)
    b = from_linear(0.0557 * x - 0.2040 * y + 1.0570 * z)

    clipped = r < 0 or r > 1 or g < 0 or g > 1 or b < 0 or b > 1

    r = clamp(r, 0, 1)
    g = clamp(g, 0, 1)
    b = clamp(b, 0, 1)

    maximum = max(r, g, b)
    minimum = min(r, g, b)
    delta = maximum - minimum

    if delta == 0:
        h = 0
    elif maximum == r:
        h = 60 * (((g - b) / delta) % 6)
    elif maximum == g:
        h = 60 * (((b - r) / delta) + 2)
    else:
        h = 60 * (((r - g) / delta) + 4)

    s = 0 if maximum == 0 else delta / maximum
    v = maximum

    return h, s * 100, v * 100, clipped
