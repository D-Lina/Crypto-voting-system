class Commissioner:
    def __init__(self):
        self.valid_n1: set[str] = set()
        self.valid_n2_fingerprints: set[str] = set()
        self.tth = ToyTetragraphHash()