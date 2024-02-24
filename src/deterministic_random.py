import hashlib, struct, typing

MASK = (1 << 32) - 1

class DeterministicRandom:
    def __init__(self, level_id: int, seed: int) -> None:
        self.level_id = level_id
        self.seed = seed
        self.sequence = 0
        self.buffer = b""

    def rand(self) -> int:
        if len(self.buffer) < 4:
            self.buffer = hashlib.sha256(struct.pack("<IIII",
                    self.level_id & MASK,
                    self.seed,
                    self.sequence & MASK,
                    0)).digest()
            self.sequence += 1
        (value, ) = struct.unpack("<I", self.buffer[:4])
        self.buffer = self.buffer[4:]
        return value

    def randrange(self, low: int, high: int) -> int:
        size = high - low
        assert size > 0
        return (self.rand() % size) + low
