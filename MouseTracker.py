import win32gui
import pyautogui

class MouseTracker:
    def __init__(self, memory_reader):
        self.memory_reader = memory_reader
        self.mouse_x = 0
        self.mouse_y = 0
        self.window_info = None
        self.hwnd = None

    def set_hwnd(self, hwnd):
        self.hwnd = hwnd
        self.update_window_info()

    def update_window_info(self):
        if self.hwnd:
            rect = win32gui.GetWindowRect(self.hwnd)
            x, y, x1, y1 = rect
            self.window_info = {
                'hwnd': self.hwnd,
                'title': win32gui.GetWindowText(self.hwnd),
                'position': (x, y),
                'size': (x1 - x, y1 - y)
            }

    def get_cursor_position_relative(self):
        self.update_window_info()  # <- Atualiza a posição da janela a cada chamada

        if not self.window_info:
            return None

        x_win, y_win = self.window_info['position']
        width, height = self.window_info['size']
        x_mouse, y_mouse = pyautogui.position()

        if x_win <= x_mouse <= x_win + width and y_win <= y_mouse <= y_win + height:
            return (x_mouse - x_win, y_mouse - y_win)
        return None

    def update(self):
        pos = self.get_cursor_position_relative()
        if pos:
            self.mouse_x, self.mouse_y = pos
        else:
            self.mouse_x, self.mouse_y = -1, -1
