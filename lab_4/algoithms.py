import numpy as np

class DiscreteGrid:
    def __init__(self, size):
        self.size = size
        self.half = size // 2
        self.grid = np.zeros((self.size, self.size))

    def set_pixel(self, x, y):
        x_idx = x + self.half
        y_idx = y + self.half
        
        if 0 <= x_idx < self.size and 0 <= y_idx < self.size:
            self.grid[x_idx, y_idx] = 1

    def clear(self):
        self.grid = np.zeros((self.size, self.size))

    def naive_drawing_algorithm(self, x_1, y_1, x_2, y_2):
        dx = x_2 - x_1
        dy = y_2 - y_1

        if dx == 0:
            y_start = min(y_1, y_2)
            y_end = max(y_1, y_2)
            for y in range(y_start, y_end + 1):
                self.set_pixel(x_1, y)
            return

        k = dy / dx
        b = y_1 - k * x_1

        if np.abs(k) > 1:
            y_start = min(y_1, y_2)
            y_end = max(y_1, y_2)
            for y in range(y_start, y_end + 1):
                x = int(np.round((y - b) / k))
                self.set_pixel(x, y)

        else:
            x_start = min(x_1, x_2)
            x_end = max(x_1, x_2)
            for x in range(x_start, x_end + 1):
                y = int(np.round(k * x + b))
                self.set_pixel(x, y)

    def dda_algorithm(self, x_1, y_1, x_2, y_2):
        dx = x_2 - x_1
        dy = y_2 - y_1
        L = np.max((np.abs(dx), np.abs(dy)))

        if L == 0:
            self.set_pixel(x_1, y_1)
            return
        
        step_x = dx / L
        step_y = dy / L

        x = float(x_1)
        y = float(y_1)

        for _ in range(L + 1):
            self.set_pixel(int(np.round(x)), int(np.round(y)))
            x += step_x
            y += step_y

    def bresenham_algorithm(self, x_1, y_1, x_2, y_2):
        dx = abs(x_2 - x_1)
        dy = abs(y_2 - y_1)
        
        sx = 1 if x_1 < x_2 else -1
        sy = 1 if y_1 < y_2 else -1
        
        err = dx - dy

        while True:
            self.set_pixel(x_1, y_1)
            
            if x_1 == x_2 and y_1 == y_2:
                break
                
            e2 = err * 2

            if e2 > -dy:
                err -= dy
                x_1 += sx

            if e2 < dx:
                err += dx
                y_1 += sy


    def get_grid(self):
        return self.grid              