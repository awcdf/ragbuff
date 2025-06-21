class PlayerStatus:
    def __init__(self, mem):
        self.mem = mem
        self.OFFSETS = {
            'hp': 0x010A075C,
            'hp_total': 0x010A0760,
            'sp': 0x010A0764,
            'sp_total': 0x010A0768,
            'x': 0x01089444,
            'y': 0x01089448,
            'map': 0x0109CC08
        }

    def get_status(self):
        try:
            return {
                'hp': self.mem.read_int(self.OFFSETS['hp']),
                'hp_total': self.mem.read_int(self.OFFSETS['hp_total']),
                'sp': self.mem.read_int(self.OFFSETS['sp']),
                'sp_total': self.mem.read_int(self.OFFSETS['sp_total']),
                'x': self.mem.read_int(self.OFFSETS['x']),
                'y': self.mem.read_int(self.OFFSETS['y']),
                'map': self.mem.read_string(self.OFFSETS['map']).strip()
            }
        except:
            return None

    def get_map_name(self):
        try:
            return self.mem.read_string(self.OFFSETS['map']).strip()
        except:
            return None
