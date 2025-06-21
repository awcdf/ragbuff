import pymem
import pymem.process
import struct

class MemoryReader:
    def __init__(self, process_name="Ragexe.exe"):
        try:
            self.pm = pymem.Pymem(process_name)
            self.base = pymem.process.module_from_name(self.pm.process_handle, process_name).lpBaseOfDll
        except Exception as e:
            print(f"[ERRO] Falha ao conectar ao processo '{process_name}': {e}")
            raise SystemExit(1)

    def read_int(self, offset):
        return self.pm.read_int(self.base + offset)

    def read_string(self, offset, max_length=16):
        raw = self.pm.read_bytes(self.base + offset, max_length)
        return raw.decode('utf-8', errors='ignore').split('\x00')[0]

    def read_bytes(self, offset, size):
        return self.pm.read_bytes(self.base + offset, size)
