import struct
import json

class BuffManager:
    def __init__(self, mem, buff_offset=0x010A0BEC, count=32, size=4):
        self.mem = mem
        self.base_offset = buff_offset
        self.count = count
        self.size = size
        with open("buffs.json", "r", encoding="utf-8") as f:
            self.buff_map = {int(k): v for k, v in json.load(f).items()}

    def get_buffs(self):
      try:
          raw = self.mem.read_bytes(self.base_offset, self.count * self.size)
          ids = struct.unpack(f"<{self.count}I", raw)
          return [
              self.buff_map.get(buff_id, f"ID {buff_id}")
              for buff_id in ids
              if buff_id != 0xFFFFFFFF and buff_id != 0
          ]
      except Exception:
          return []
