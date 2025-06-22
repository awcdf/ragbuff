import tkinter as tk
from tkinter import ttk
import win32gui
import win32process
import pymem

class WindowSelector(ttk.Frame):
    def __init__(self, parent, MemoryReaderClass, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.memory_reader_cls = MemoryReaderClass
        self.windows = []
        self.selected_window = None

        self.combo = ttk.Combobox(self, state="readonly", width=60)
        self.combo.pack(pady=(5, 2))
        self.combo.bind("<<ComboboxSelected>>", self.on_select)

        self.btn_refresh = ttk.Button(self, text="Atualizar", command=self.refresh)
        self.btn_refresh.pack()

        self.refresh()

    def refresh(self):
        self.windows = []
        result = []

        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "Ragnarok" in title:
                    try:
                        pid = win32process.GetWindowThreadProcessId(hwnd)[1]
                        pm = pymem.Pymem()
                        pm.open_process_from_id(pid)
                        module = pymem.process.module_from_name(pm.process_handle, "Ragexe.exe")
                        if module:
                            char_name = pm.read_bytes(module.lpBaseOfDll + 0x010a2ff8, 24).decode('utf-8', 'ignore').split('\x00')[0]
                            x, y, x1, y1 = win32gui.GetWindowRect(hwnd)
                            result.append({
                                'hwnd': hwnd,
                                'pid': pid,
                                'title': title,
                                'char_name': char_name,
                                'position': (x, y),
                                'size': (x1 - x, y1 - y)
                            })
                    except Exception:
                        pass

        win32gui.EnumWindows(callback, None)
        self.windows = result
        names = [f"{w['char_name']} - PID: {w['pid']}" for w in self.windows]
        self.combo['values'] = names

        if names:
            self.combo.current(0)
            self.selected_window = self.windows[0]

    def on_select(self, event=None):
        index = self.combo.current()
        if index >= 0 and index < len(self.windows):
            self.selected_window = self.windows[index]
