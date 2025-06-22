from tkinter import ttk, Canvas
from PIL import Image, ImageTk
import os
import struct
import numpy as np
import gzip
import io


class MapViewer:
    def __init__(self, parent, maps_folder='mapas'):
        self.maps_folder = maps_folder
        self.parent = parent
        self.frame = ttk.LabelFrame(parent, text="MAPA")

        # Definindo canvas sem tamanho fixo para poder ajustar dinamicamente
        self.canvas = Canvas(self.frame)
        self.canvas.pack(fill="both", expand=True)

        self.current_map_name = None
        self.map_image = None
        self.marker = None

        self.width = 0
        self.height = 0
        self.data = None

        # Bind para redimensionar mapa quando canvas muda de tamanho
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self._resized_img = None  # Para manter a referência da imagem redimensionada

        # Guarda a última posição para redesenhar marcador após redimensionar
        self._last_marker_pos = None

    def load_map(self, map_name):
        gz_path = os.path.join(self.maps_folder, f"{map_name}.fld2.gz")
        if not os.path.exists(gz_path):
            print(f"[MapViewer] Arquivo do mapa não encontrado: {gz_path}")
            self.current_map_name = None
            self.data = None
            self.width = 0
            self.height = 0
            self.map_image = None
            self.canvas.delete("all")
            return False

        try:
            with gzip.open(gz_path, 'rb') as gz_file:
                fld2_data = gz_file.read()
                with io.BytesIO(fld2_data) as f:
                    self.width, self.height = struct.unpack('<HH', f.read(4))
                    raw_data = f.read(self.width * self.height)
                    map_data = np.frombuffer(raw_data, dtype=np.uint8).reshape((self.height, self.width))
                    self.data = np.flipud(map_data)
            self.current_map_name = map_name
            return True
        except Exception as e:
            print(f"[MapViewer] Erro ao carregar mapa {map_name}: {e}")
            self.current_map_name = None
            self.data = None
            self.width = 0
            self.height = 0
            self.map_image = None
            self.canvas.delete("all")
            return False

    def get_image(self):
        if self.data is None:
            return None

        # Cria imagem grayscale invertendo o dado do mapa
        img = Image.fromarray(255 - self.data * 255)
        # Não rotaciona mais
        return img

    def adjust_coordinates(self, x, y):
        # Ajuste simples: inverte eixo Y para coordenadas no canvas (opcional, se precisar)
        new_x = x
        new_y = self.height - y
        return new_x, new_y

    def update_map(self, map_name, x, y):
        # Se mapa mudou, carrega o novo
        if map_name != self.current_map_name:
            success = self.load_map(map_name)
            if not success:
                return

        if self.data is None:
            self.canvas.delete("all")
            return

        # Pega a imagem base
        img = self.get_image()
        if img is None:
            self.canvas.delete("all")
            return

        # Pega tamanho atual do canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas ainda não foi dimensionado, ignora atualização agora
            return

        # Redimensiona imagem para encaixar no canvas
        resized_img = img.resize((canvas_width, canvas_height), Image.NEAREST)
        self._resized_img = ImageTk.PhotoImage(resized_img)

        # Desenha imagem no canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self._resized_img)

        # Ajusta coordenadas do player para escala do canvas
        adj_x, adj_y = self.adjust_coordinates(x, y)
        scale_x = canvas_width / self.width
        scale_y = canvas_height / self.height
        canvas_x = adj_x * scale_x
        canvas_y = adj_y * scale_y

        # Desenha marcador no canvas
        radius = 3
        self.marker = self.canvas.create_oval(
            canvas_x - radius, canvas_y - radius, canvas_x + radius, canvas_y + radius, fill="red"
        )

        # Guarda última posição pra poder redesenhar se necessário
        self._last_marker_pos = (map_name, x, y)

    def on_canvas_resize(self, event):
        # Quando o canvas muda de tamanho, redesenha o mapa e o marcador, se possível
        if self._last_marker_pos:
            map_name, x, y = self._last_marker_pos
            self.update_map(map_name, x, y)
