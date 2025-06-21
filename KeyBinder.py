import json
import os
import pyautogui
import tkinter as tk
from tkinter import ttk
import win32gui

class KeyBinder(ttk.Frame):
    def __init__(self, master=None, bind_count=10):
        super().__init__(master)
        self.bind_count = bind_count
        self.entries = []
        self.combos = []
        self.keybindings_file = "keybindings.json"
        self.buff_list = self.load_buff_list()
        self.build_ui()
        self.load_bindings_from_file()

    def load_buff_list(self):
        try:
            with open('buffs.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            return list(data.values())
        except Exception as e:
            print(f"[ERRO] Falha ao carregar buffs.json: {e}")
            return []

    def build_ui(self):
        # Cria o frame principal dividido em esquerda e direita
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="y", padx=10)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=10)

        self.map_frame = right_frame  # <- necessário para MapViewerGZ usar

        # Seções de entrada de teclas e combos
        for i in range(self.bind_count):
            frame = ttk.Frame(left_frame)
            frame.pack(fill="x", pady=2)

            entry = ttk.Entry(frame, width=10)
            entry.pack(side="left", padx=(0, 5))
            entry.bind("<FocusIn>", lambda e, idx=i: self.capture_key(e, idx))
            entry.bind("<Key>", self.block_typing)
            self.entries.append(entry)

            combo = ttk.Combobox(frame, values=self.buff_list, state="normal", width=25)
            combo.pack(side="left")
            combo.bind("<KeyRelease>", self.filter_combo)
            self.combos.append(combo)

        button_frame = ttk.Frame(left_frame)
        button_frame.pack(pady=5)

        save_btn = ttk.Button(button_frame, text="Salvar Configurações", command=self.save_bindings_to_file)
        save_btn.pack(side="left", padx=5)

        clear_btn = ttk.Button(button_frame, text="Limpar", command=self.clear_all_bindings)
        clear_btn.pack(side="left", padx=5)

    def block_typing(self, event):
        return "break"

    def capture_key(self, event, index):
        def on_key_press(e):
            key = e.keysym
            self.entries[index].delete(0, tk.END)
            self.entries[index].insert(0, key)
            self.entries[index].unbind("<Key>", on_key_press_id)

        on_key_press_id = self.entries[index].bind("<Key>", on_key_press)

    def get_key_bindings(self):
        bindings = []
        for entry, combo in zip(self.entries, self.combos):
            key = entry.get().lower().strip()
            buff = combo.get()
            bindings.append((key, buff))
        return bindings

    def save_bindings_to_file(self):
        data = self.get_key_bindings()
        try:
            with open(self.keybindings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print("[INFO] Configurações salvas em keybindings.json")
        except Exception as e:
            print(f"[ERRO] Falha ao salvar configurações: {e}")

    def load_bindings_from_file(self):
        if not os.path.exists(self.keybindings_file):
            return
        try:
            with open(self.keybindings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for i, (key, buff) in enumerate(data):
                if i >= self.bind_count:
                    break
                self.entries[i].delete(0, tk.END)
                self.entries[i].insert(0, key)
                if buff in self.buff_list:
                    self.combos[i].set(buff)
        except Exception as e:
            print(f"[ERRO] Falha ao carregar keybindings.json: {e}")

    def clear_all_bindings(self):
        for entry, combo in zip(self.entries, self.combos):
            entry.delete(0, tk.END)
            combo.set("")
        print("[INFO] Todos os bindings foram limpos")

    def send_key_to_ragnarok(self, key_name: str):
        try:
            if not self.is_ragnarok_window_active():
                print("[INFO] Janela do Ragnarok não está ativa. Ignorando envio de tecla.")
                return
            key = self.map_key_name(key_name)
            if key:
                pyautogui.press(key)
                print(f"[INFO] Tecla '{key}' enviada via pyautogui")
            else:
                print(f"[WARN] Tecla '{key_name}' não mapeada para pyautogui")
        except Exception as e:
            print(f"[ERRO] Falha ao enviar tecla '{key_name}': {e}")

    def is_ragnarok_window_active(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            return "Ragnarok" in title
        except Exception as e:
            print(f"[ERRO] Falha ao verificar janela ativa: {e}")
            return False

    def map_key_name(self, key_name: str) -> str:
        return key_name.lower()

    def filter_combo(self, event):
        widget = event.widget
        value = widget.get().lower()
        filtered = [buff for buff in self.buff_list if value in buff.lower()]
        widget['values'] = filtered
