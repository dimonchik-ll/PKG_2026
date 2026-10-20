import numpy as np

radius = 2
data = np.array([[1, 2, 3],
                 [4, 5, 6],
                 [7, 8, 9]])

height, width = 3, 3
padded = np.zeros((7, 7))
pad_h, pad_w = 7, 7

padded[radius : radius + height, radius : radius + width] = data

for y in range(radius):
    padded[y, radius : radius + width] = data[radius - y, :]
    padded[pad_h - y - 1, radius : radius + width] = data[-radius + y - 1, :]

for x in range(radius):
    padded[:, x] = padded[:, 2 * radius - x]
    padded[:, pad_w - x - 1] = padded[:, -2 * radius + x - 1]

print(padded)