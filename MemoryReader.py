import pymem
import pymem.process
import struct

class MemoryReader:
    def __init__(self, process):
        try:
            if isinstance(process, int):
                self.pm = pymem.Pymem()
                self.pm.open_process_from_id(process)
                module = pymem.process.module_from_name(self.pm.process_handle, "Ragexe.exe")
                if not module:
                    raise Exception("Módulo 'Ragexe.exe' não encontrado.")
                self.base = module.lpBaseOfDll
            else:
                self.pm = pymem.Pymem(process)
                module = pymem.process.module_from_name(self.pm.process_handle, process)
                if not module:
                    raise Exception(f"Módulo '{process}' não encontrado.")
                self.base = module.lpBaseOfDll
        except Exception as e:
            print(f"[ERRO] Falha ao conectar ao processo '{process}': {e}")
            raise SystemExit(1)

    def read_int(self, offset):
        return self.pm.read_int(self.base + offset)

    def read_string(self, offset, max_length=16):
        raw = self.pm.read_bytes(self.base + offset, max_length)
        return raw.decode('utf-8', errors='ignore').split('\x00')[0]

    def read_bytes(self, offset, size):
        return self.pm.read_bytes(self.base + offset, size)
