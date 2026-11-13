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

    def bresenham_circle(self, cx, cy, r):
        x = 0
        y = r
        d = 3 - 2 * r

        while (x <= y):
            self._draw_circle_symmetry(cx, cy, x, y)

            x += 1
            if d < 0:
                d = d + 4 * x + 6
            else:
                y = y - 1
                d = d + 4 * (x - y) + 6

    def castle_pitteway_ellipse(self, cx, cy, a, b):
        x = 0
        y = b
        
        a2 = a * a
        b2 = b * b
        
        K1 = 2 * b2
        K2 = 2 * a2
        
        dx = 0
        dy = K2 * y
        
        d1 = round(b2 - (a2 * b) + (0.25 * a2)) 
        
        while dx < dy:
            self._draw_conic_symmetry(cx, cy, x, y)
            
            x += 1
            dx += K1
            
            if d1 < 0:
                d1 += dx + b2
            else:
                y -= 1
                dy -= K2
                d1 += dx - dy + b2
                
        d2 = round(b2 * (x + 0.5)**2 + a2 * (y - 1)**2 - a2 * b2)
        
        while y >= 0:
            self._draw_conic_symmetry(cx, cy, x, y)
            
            y -= 1
            dy -= K2
            
            if d2 > 0:
                d2 += a2 - dy
            else:
                x += 1
                dx += K1
                d2 += dx - dy + a2

    def _draw_circle_symmetry(self, cx, cy, x, y):
        self.set_pixel(cx + x, cy + y)
        self.set_pixel(cx - x, cy + y)
        self.set_pixel(cx + x, cy - y)
        self.set_pixel(cx - x, cy - y)
        self.set_pixel(cx + y, cy + x)
        self.set_pixel(cx - y, cy + x)
        self.set_pixel(cx + y, cy - x)
        self.set_pixel(cx - y, cy - x)

    def _draw_conic_symmetry(self, cx, cy, x, y):
        self.set_pixel(cx + x, cy + y)
        self.set_pixel(cx - x, cy + y)
        self.set_pixel(cx + x, cy - y)
        self.set_pixel(cx - x, cy - y)


    def get_grid(self):
        return self.grid              