import tkinter as tk
from tkinter import ttk, messagebox
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
        self.map_viewer.frame.configure(height=210)

        self.found_windows = []  # Lista de (hwnd, title, pid, char_name)
        self.ui_job = None

        self.build_ui()
        self.root.after(100, self.update_window_list)

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
        print("[DEBUG] Atualizando lista de janelas...")
        windows = []
        ragexe_pids = {proc.pid for proc in psutil.process_iter(['pid', 'name'])
                       if proc.info['name'] and proc.info['name'].lower() == 'ragexe.exe'}

        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid in ragexe_pids:
                    title = win32gui.GetWindowText(hwnd)
                    windows.append((hwnd, title, pid))
                    ragexe_pids.discard(pid)

        win32gui.EnumWindows(callback, None)

        found = []
        combo_values = []

        for hwnd, title, pid in windows:
            char_name = "???"
            try:
                mem = MemoryReader(pid=pid)
                tmp_status = PlayerStatus(mem)
                char_name = tmp_status.get_name()
            except Exception as e:
                print(f"[DEBUG] Erro ao obter nome do personagem PID {pid}: {e}")

            found.append((hwnd, title, pid, char_name))
            combo_values.append(char_name)

        self.found_windows = found
        self.window_combo['values'] = combo_values

        if combo_values:
            self.window_combo.current(0)
            self.window_var.set(combo_values[0])
            self.try_auto_connect_by_name(combo_values[0])
        else:
            self.window_combo.set("")
            self.window_var.set("")

        print("[DEBUG] ComboBox values:", combo_values)

    def try_auto_connect_by_name(self, char_name):
        match = next(((h, t, p, c) for h, t, p, c in self.found_windows if c == char_name), None)
        if not match:
            return

        hwnd, _, pid, _ = match
        try:
            self.memory_reader = MemoryReader(pid=pid)
            self.status = PlayerStatus(self.memory_reader)
            self.mouse_tracker = MouseTracker(self.memory_reader)
            self.mouse_tracker.set_hwnd(hwnd)
            self.buff_manager = BuffManager(self.memory_reader)
            if self.ui_job:
                self.root.after_cancel(self.ui_job)
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Erro ao conectar", f"Falha ao conectar ao processo 'Ragexe.exe':\n{str(e)}")
            self.root.destroy()

    def on_window_selected(self, event):
        selected_name = self.window_combo.get()
        if not selected_name:
            return

        match = next(((h, t, p, c) for h, t, p, c in self.found_windows if c == selected_name), None)
        if not match:
            return

        hwnd, _, pid, _ = match

        self.memory_reader = MemoryReader(pid=pid)
        self.status = PlayerStatus(self.memory_reader)
        self.mouse_tracker = MouseTracker(self.memory_reader)
        self.mouse_tracker.set_hwnd(hwnd)
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
