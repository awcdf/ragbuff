import tkinter as tk
from tkinter import ttk
import win32gui
import win32process
import psutil

from MapViewer import MapViewer
from MemoryReader import MemoryReader
from PlayerStatus import PlayerStatus
from MouseTracker import MouseTracker
from BuffManager import BuffManager
from KeyBinder import KeyBinder


class MainApp:
    def __init__(self, root):
        self.root = root
        self.memory_reader = None
        self.status = None
        self.mouse_tracker = None
        self.buff_manager = None
        self.key_binder = KeyBinder()
        self.map_viewer = MapViewer(self.root)
        self.map_viewer.frame.grid(row=0, column=1, rowspan=5, padx=10, pady=10, sticky="nsew")

        self.found_windows = []  # Lista de (hwnd, title, pid)
        self.ui_job = None

        self.build_ui()
        self.update_window_list()

    def build_ui(self):
        self.root.title("RagBuff")

        self.window_frame = ttk.LabelFrame(self.root, text="Selecionar Janela")
        self.window_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")

        self.window_label = ttk.Label(self.window_frame, text="Janela:")
        self.window_label.pack(anchor="w", padx=5, pady=(5, 0))

        self.window_var = tk.StringVar()
        self.window_combo = ttk.Combobox(self.window_frame, textvariable=self.window_var, state="readonly", width=30)
        self.window_combo['values'] = []
        self.window_combo.pack(anchor="w", padx=5, pady=(0, 5))
        self.window_combo.bind("<<ComboboxSelected>>", self.on_window_selected)

        self.update_button = ttk.Button(self.window_frame, text="Atualizar", command=self.update_window_list)
        self.update_button.pack(anchor="w", padx=5, pady=(0, 5))

        self.status_frame = ttk.LabelFrame(self.root, text="STATUS")
        self.status_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.hp_label = ttk.Label(self.status_frame, text="HP: --")
        self.hp_label.pack(anchor="w", padx=5)
        self.sp_label = ttk.Label(self.status_frame, text="SP: --")
        self.sp_label.pack(anchor="w", padx=5)

        self.location_frame = ttk.LabelFrame(self.root, text="LOCALIZAÇÃO")
        self.location_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.map_label = ttk.Label(self.location_frame, text="Mapa: --")
        self.map_label.pack(anchor="w", padx=5)
        self.coords_label = ttk.Label(self.location_frame, text="Coordenadas: --")
        self.coords_label.pack(anchor="w", padx=5)

        self.buff_frame = ttk.LabelFrame(self.root, text="BUFFS ATIVOS")
        self.buff_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        self.buff_text = tk.Text(self.buff_frame, height=10, width=40)
        self.buff_text.pack(padx=5, pady=5)

        self.cursor_frame = ttk.LabelFrame(self.root, text="CURSOR DO MOUSE")
        self.cursor_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
        self.cursor_label = ttk.Label(self.cursor_frame, text="Posição do Mouse: --")
        self.cursor_label.pack(anchor="w", padx=5)

    def update_window_list(self):
        windows = []
        ragexe_pids = {proc.pid for proc in psutil.process_iter(['pid', 'name']) if proc.info['name'] and proc.info['name'].lower() == 'ragexe.exe'}

        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid in ragexe_pids:
                    title = win32gui.GetWindowText(hwnd)
                    windows.append((hwnd, title, pid))

        win32gui.EnumWindows(callback, None)
        self.found_windows = windows
        self.window_combo['values'] = [f"{hwnd} - {title}" for hwnd, title, _ in windows]
        if windows:
            self.window_combo.current(0)

    def on_window_selected(self, event):
        selection = self.window_combo.get()
        if not selection:
            return

        hwnd_str = selection.split(" - ")[0]
        try:
            hwnd = int(hwnd_str)
        except ValueError:
            return

        match = next(((h, t, p) for h, t, p in self.found_windows if h == hwnd), None)
        if not match:
            return

        _, _, pid = match
        self.memory_reader = MemoryReader(pid=pid)
        self.status = PlayerStatus(self.memory_reader)
        self.mouse_tracker = MouseTracker(self.memory_reader)
        self.buff_manager = BuffManager(self.memory_reader)

        if self.ui_job:
            self.root.after_cancel(self.ui_job)

        self.update_ui()

    def update_ui(self):
        if self.status is None:
            self.hp_label.config(text="HP: --")
            self.sp_label.config(text="SP: --")
            self.map_label.config(text="Mapa: --")
            self.coords_label.config(text="Coordenadas: --")
            self.cursor_label.config(text="Posição do Mouse: --")
            self.buff_text.delete(1.0, tk.END)
            self.ui_job = self.root.after(500, self.update_ui)
            return

        status_data = self.status.get_status()
        if status_data:
            self.hp_label.config(text=f"HP: {status_data['hp']} / {status_data['hp_total']}")
            self.sp_label.config(text=f"SP: {status_data['sp']} / {status_data['sp_total']}")
            self.map_label.config(text=f"Mapa: {status_data['map']}")
            self.coords_label.config(text=f"Coordenadas: {status_data['x']}, {status_data['y']}")
            self.map_viewer.update_map(status_data['map'], status_data['x'], status_data['y'])

        pos = self.mouse_tracker.get_cursor_position_relative() if self.mouse_tracker else None
        if pos:
            self.cursor_label.config(text=f"Posição do Mouse: {pos[0]}, {pos[1]}")
        else:
            self.cursor_label.config(text="Posição do Mouse: Fora da janela")

        buffs = self.buff_manager.get_buffs() if self.buff_manager else []
        self.buff_text.delete(1.0, tk.END)
        for buff in buffs:
            self.buff_text.insert(tk.END, f"{buff}\n")

        self.ui_job = self.root.after(500, self.update_ui)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
