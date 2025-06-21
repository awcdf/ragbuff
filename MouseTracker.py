import win32gui
import pyautogui

class MouseTracker:
    def __init__(self):
        self.hwnd = None
        self.window_info = None

    def get_window(self):
        def callback(hwnd, result):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "Ragnarok" in title:
                    rect = win32gui.GetWindowRect(hwnd)
                    x, y, x1, y1 = rect
                    result.append({'hwnd': hwnd, 'title': title, 'position': (x, y), 'size': (x1 - x, y1 - y)})
        result = []
        win32gui.EnumWindows(callback, result)
        if result:
            self.window_info = result[0]
            self.hwnd = result[0]['hwnd']
            return result[0]
        return None

    def get_cursor_position_relative(self):
        self.get_window()  # Atualiza info da janela a cada chamada
        if not self.window_info:
            return None
        x_win, y_win = self.window_info['position']
        width, height = self.window_info['size']
        x_mouse, y_mouse = pyautogui.position()
        if x_win <= x_mouse <= x_win + width and y_win <= y_mouse <= y_win + height:
            return (x_mouse - x_win, y_mouse - y_win)
        return None
