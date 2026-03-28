"""
tth_hash.py
Toy Tetragraph Hash (TTH) - Implémentation pour le projet de vote électronique
"""
print("TTH FILE LOADED")

class ToyTetragraphHash:
    """Toy Tetragraph Hash - Version pour le projet de vote"""
    
    def __init__(self):
        self.alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        self.modulus = len(self.alphabet)
        
        self.char_to_num = {c: i for i, c in enumerate(self.alphabet)}
        self.num_to_char = {i: c for i, c in enumerate(self.alphabet)}
        
        self.matrix = [
            [1, 1, 0, 1],
            [1, 0, 1, 0],
            [0, 1, 1, 1],
            [1, 0, 0, 1],
        ]
        
        self.initial_state = [0, 0, 0, 0]
    
    def _code_to_numbers(self, code: str) -> list:
        code = code.upper().replace(" ", "").replace("-", "")
        
        numbers = []
        for char in code:
            if char not in self.char_to_num:
                raise ValueError(f"Caractère invalide: '{char}'. Utilisez A-Z et 0-9.")
            numbers.append(self.char_to_num[char])
        
        return numbers
    
    def _numbers_to_code(self, numbers: list) -> str:
        return ''.join(self.num_to_char[n] for n in numbers)
    
    def _pad_message(self, numbers: list) -> list:
        b = 4
        original_length = len(numbers)
        
        numbers.append(self.modulus - 1)
        
        padding_needed = (b - ((len(numbers) + 1) % b)) % b
        numbers.extend([0] * padding_needed)
        
        length_block = [
            (original_length // 1000) % self.modulus,
            (original_length // 100) % self.modulus,
            (original_length // 10) % self.modulus,
            original_length % self.modulus
        ]
        numbers.extend(length_block)
        
        return numbers
    
    def _compression_function(self, state: list, block: list) -> list:
        combined = [
            (state[i] + block[i]) % self.modulus
            for i in range(4)
        ]
        
        new_state = [0, 0, 0, 0]
        for i in range(4):
            for j in range(4):
                new_state[i] += self.matrix[i][j] * combined[j]
            new_state[i] %= self.modulus
        
        return new_state
    
    # ✅ FIX ICI
    def hash(self, code: str) -> str:
        if not code or code.isspace():
            return "AAAA"
        
        numbers = self._code_to_numbers(code)
        padded = self._pad_message(numbers)
        
        blocks = []
        for i in range(0, len(padded), 4):
            block = padded[i:i+4]
            
            while len(block) < 4:
                block.append(0)
            
            blocks.append(block)

        state = self.initial_state.copy()
        for block in blocks:
            state = self._compression_function(state, block)
        
        return self._numbers_to_code(state)
    
    def verify(self, code: str, fingerprint: str) -> bool:
        return self.hash(code) == fingerprint
    
    def hash_hex(self, code: str) -> str:
        h = self.hash(code)
        return ''.join(hex(self.char_to_num[c])[2:].zfill(2) for c in h)
 
