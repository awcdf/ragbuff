import struct
import numpy as np
from PIL import Image
import gzip
import io
import os

class MapViewer:
    def __init__(self, map_name, maps_folder='mapas'):
        self.maps_folder = maps_folder
        self.map_name = map_name
        self.width = 0
        self.height = 0
        self.data = None

        self.load_map_from_gz()

    def load_map_from_gz(self):
        gz_path = os.path.join(self.maps_folder, f"{self.map_name}.fld2.gz")
        fld2_filename = f"{self.map_name}.fld2"

        if not os.path.exists(gz_path):
            print(f"[ERRO] Arquivo {gz_path} não encontrado.")
            return

        try:
            with gzip.open(gz_path, 'rb') as gz_file:
                gz_content = gz_file.read()

                # Procurar por arquivo interno com mesmo nome
                start = gz_content.find(b'\x00' * 4)  # Tentativa de localização — alternativa abaixo
                fld2_data = gz_content

                # Abre o conteúdo do fld2 como se fosse arquivo em memória
                with io.BytesIO(fld2_data) as f:
                    self.width, self.height = struct.unpack('<HH', f.read(4))
                    data = f.read(self.width * self.height)
                    map_data = np.frombuffer(data, dtype=np.uint8).reshape((self.height, self.width))
                    self.data = np.flipud(map_data)
        except Exception as e:
            print(f"[ERRO] Falha ao carregar mapa {fld2_filename} de {gz_path}: {e}")

    def get_image(self):
        if self.data is None:
            return Image.new("L", (100, 100), color=128)  # mapa neutro
        image = Image.fromarray(255 - self.data * 255).transpose(Image.FLIP_TOP_BOTTOM)
        return image
