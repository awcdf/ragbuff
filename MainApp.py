import tkinter as tk
from tkinter import ttk, Canvas
from PIL import ImageTk
import ctypes
import time

from MemoryReader import MemoryReader
from PlayerStatus import PlayerStatus
from BuffManager import BuffManager
from MouseTracker import MouseTracker
from MapViewer import MapViewer
from KeyBinder import KeyBinder

def send_input_key(key_name):
    vk_codes = {
        'F1': 0x70, 'F2': 0x71, 'F3': 0x72, 'F4': 0x73,
        'F5': 0x74, 'F6': 0x75, 'F7': 0x76, 'F8': 0x77,
        'F9': 0x78, 'F10': 0x79, 'F11': 0x7A, 'F12': 0x7B,
        '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35,
        '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39, '0': 0x30,
        'A': 0x41, 'B': 0x42, 'C': 0x43, 'D': 0x44, 'E': 0x45,
        # Adicione mais teclas conforme necessidade
    }

    key = key_name.upper()
    if key not in vk_codes:
        print(f"[ERRO] Tecla '{key}' não suportada.")
        return

    vk = vk_codes[key]
    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(vk, 0, 2, 0)


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor Ragnarok")
        self.root.geometry("1000x800")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2f")

        self.mem = MemoryReader()
        self.status = PlayerStatus(self.mem)
        self.buffs = BuffManager(self.mem)
        self.mouse = MouseTracker()
        self.scale = 1
        self.rodando = True

        self.current_map_name = self.status.get_map_name() or "unknown_map"
        self.map_viewer = MapViewer(self.current_map_name)

        self.build_ui()
        self.load_map_image()
        self.update_loop()
        self.track_mouse()
        self.update_map()
        self.verificar_e_ativar_buffs()

    def build_ui(self):
        style = ttk.Style()
        style.configure("TLabel", font=("Segoe UI", 11), background="#1e1e2f", foreground="white")
        style.configure("TFrame", background="#1e1e2f")
        style.configure("TLabelFrame", background="#1e1e2f", foreground="white", font=("Segoe UI", 11, "bold"))

        container = ttk.Frame(self.root, padding="10")
        container.pack(fill="both", expand=True)

        self.main_frame = ttk.Frame(container)
        self.main_frame.pack(side=tk.LEFT, fill="y")

        stats_frame = ttk.LabelFrame(self.main_frame, text="Status")
        stats_frame.pack(fill="x", padx=5, pady=5)
        self.label_hp = ttk.Label(stats_frame, text="HP: ")
        self.label_hp.pack(anchor="w")
        self.label_sp = ttk.Label(stats_frame, text="SP: ")
        self.label_sp.pack(anchor="w")

        pos_frame = ttk.LabelFrame(self.main_frame, text="Localização")
        pos_frame.pack(fill="x", padx=5, pady=5)
        self.label_xy = ttk.Label(pos_frame, text="Posição: ")
        self.label_xy.pack(anchor="w")
        self.label_mapa = ttk.Label(pos_frame, text="Mapa: ")
        self.label_mapa.pack(anchor="w")

        buffs_frame = ttk.LabelFrame(self.main_frame, text="Buffs Ativos")
        buffs_frame.pack(fill="x", padx=5, pady=5)
        self.buffs_text = tk.StringVar()
        self.label_buffs = ttk.Label(buffs_frame, textvariable=self.buffs_text, justify="left")
        self.label_buffs.pack(fill="x")

        mouse_frame = ttk.LabelFrame(self.main_frame, text="Cursor do Mouse")
        mouse_frame.pack(fill="x", padx=5, pady=5)
        self.label_mouse = ttk.Label(mouse_frame, text="CursorMouse x=0, y=0")
        self.label_mouse.pack(anchor="w")

        self.keybinder = KeyBinder(self.main_frame)
        self.keybinder.pack(fill="x", padx=5, pady=10)

        self.btn_toggle = ttk.Button(self.main_frame, text="Stop (Estado: Rodando)", command=self.toggle_execucao)
        self.btn_toggle.pack(fill="x", padx=5, pady=(0, 10))

        self.btn_save = ttk.Button(self.main_frame, text="Salvar configurações", command=self.salvar_configuracoes)
        self.btn_save.pack(fill="x", padx=5, pady=(0, 10))

        # Mapa ao lado direito
        map_container = ttk.Frame(container)
        map_container.pack(side=tk.RIGHT, fill="both", expand=True)

        self.canvas = Canvas(map_container, width=300, height=300, bg="#2a2a3f", highlightbackground="#999")
        self.canvas.pack(padx=5, pady=5)

    def load_map_image(self):
        map_img = self.map_viewer.get_image()
        resized = map_img.resize((map_img.width * self.scale, map_img.height * self.scale), ImageTk.Image.NEAREST)
        self.map_imgtk = ImageTk.PhotoImage(resized)
        self.canvas.config(width=resized.width, height=resized.height)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.map_imgtk)
        self.marker = self.canvas.create_oval(0, 0, 0, 0, fill='#ff4b4b', outline='black')

    def update_loop(self):
        try:
            s = self.status.get_status()
            if s:
                self.label_hp.config(text=f"HP: {s['hp']} / {s['hp_total']}")
                self.label_sp.config(text=f"SP: {s['sp']} / {s['sp_total']}")
                self.label_xy.config(text=f"Posição: ({s['x']}, {s['y']})")
                self.label_mapa.config(text=f"Mapa: {s['map']}")
            else:
                self.label_hp.config(text="HP: [erro]")
                self.label_sp.config(text="SP: [erro]")
                self.label_xy.config(text="Posição: [erro]")
                self.label_mapa.config(text="Mapa: [erro]")

            buffs = self.buffs.get_buffs()
            self.buffs_text.set("\n".join(buffs) if buffs else "Nenhum buff ativo.")
        except Exception as e:
            print(f"[ERRO] update_loop: {e}")

        self.root.after(1000, self.update_loop)

    def track_mouse(self):
        pos = self.mouse.get_cursor_position_relative()
        if pos:
            self.label_mouse.config(text=f"CursorMouse x={pos[0]}, y={pos[1]}")
        else:
            self.label_mouse.config(text="Mouse fora da janela do Ragnarok.")
        self.root.after(500, self.track_mouse)

    def update_map(self):
        try:
            pos = self.status.get_status()
            new_map = self.status.get_map_name()

            if new_map and new_map != self.current_map_name:
                print(f"[INFO] Mudança de mapa detectada: {self.current_map_name} -> {new_map}")
                self.current_map_name = new_map
                self.map_viewer = MapViewer(new_map)
                self.load_map_image()

            if pos:
                x = pos['x'] * self.scale
                y = pos['y'] * self.scale
                self.canvas.coords(self.marker, x - 3, y - 3, x + 3, y + 3)
        except Exception as e:
            print(f"[ERRO] update_map: {e}")
        self.root.after(200, self.update_map)

    def verificar_e_ativar_buffs(self):
        if not self.rodando:
            self.root.after(2000, self.verificar_e_ativar_buffs)
            return

        try:
            buffs_ativos = self.buffs.get_buffs()
            bindings = self.keybinder.get_key_bindings()

            for tecla, buff_nome in bindings:
                if not tecla or not buff_nome:
                    continue
                if buff_nome not in buffs_ativos:
                    print(f"[INFO] Buff {buff_nome} não está ativo. Ativando com tecla {tecla}")
                    send_input_key(tecla)
        except Exception as e:
            print(f"[ERRO] verificação de buff: {e}")

        self.root.after(2000, self.verificar_e_ativar_buffs)

    def toggle_execucao(self):
        self.rodando = not self.rodando
        estado = "Rodando" if self.rodando else "Parado"
        self.btn_toggle.config(text=f"{'Stop' if self.rodando else 'Start'} (Estado: {estado})")

    def salvar_configuracoes(self):
        self.keybinder.save_bindings_to_file()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
