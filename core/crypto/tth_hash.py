"""
tth_hash.py
Toy Tetragraph Hash (TTH) - Implémentation pour le projet de vote électronique
"""

class ToyTetragraphHash:
    """Toy Tetragraph Hash - Version pour le projet de vote"""
    
    def __init__(self):
        # Alphabet: 26 lettres + 10 chiffres = 36 caractères
        self.alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        self.modulus = len(self.alphabet)  # 36
        
        # Table de conversion caractère → nombre
        self.char_to_num = {c: i for i, c in enumerate(self.alphabet)}
        
        # Table de conversion nombre → caractère
        self.num_to_char = {i: c for i, c in enumerate(self.alphabet)}
        
        # Matrice de transformation 4×4 (mod 36)
        self.matrix = [
            [1, 1, 0, 1],
            [1, 0, 1, 0],
            [0, 1, 1, 1],
            [1, 0, 0, 1],
        ]
        
        # Valeur initiale (IV)
        self.initial_state = [0, 0, 0, 0]
    
    def _code_to_numbers(self, code: str) -> list:
        """Convertit un code en liste de nombres"""
        code = code.upper().replace(" ", "").replace("-", "")
        
        numbers = []
        for char in code:
            if char not in self.char_to_num:
                raise ValueError(f"Caractère invalide: '{char}'. Utilisez A-Z et 0-9.")
            numbers.append(self.char_to_num[char])
        
        return numbers
    
    def _numbers_to_code(self, numbers: list) -> str:
        """Convertit une liste de nombres en code"""
        return ''.join(self.num_to_char[n] for n in numbers)
    
    def _pad_message(self, numbers: list) -> list:
        """
        Correct padding to ensure length is multiple of 4
        """
        b = 4

        # Add end marker
        numbers.append(self.modulus - 1)

        # Add zeros until length is multiple of 4
        while len(numbers) % b != 0:
            numbers.append(0)

        return numbers

    def _compression_function(self, state: list, block: list) -> list:
        """Fonction de compression avec matrice"""
        # Combiner état et bloc
        combined = [
            (state[i] + block[i]) % self.modulus
            for i in range(4)
        ]
        
        # Appliquer la matrice
        new_state = [0, 0, 0, 0]
        for i in range(4):
            for j in range(4):
                new_state[i] += self.matrix[i][j] * combined[j]
            new_state[i] %= self.modulus
        
        return new_state
    
    def hash(self, code: str) -> str:
        """Calcule le hash TTH d'un code"""
        if not code or code.isspace():
            return "AAAA"
        
        numbers = self._code_to_numbers(code)
        padded = self._pad_message(numbers)
        
        blocks = [padded[i:i+4] for i in range(0, len(padded), 4)]
        
        state = self.initial_state.copy()
        for block in blocks:
            state = self._compression_function(state, block)
        
        return self._numbers_to_code(state)
    
    def verify(self, code: str, fingerprint: str) -> bool:
        """Vérifie si un code correspond à une empreinte"""
        return self.hash(code) == fingerprint
    
    def hash_hex(self, code: str) -> str:
        """Retourne le hash en hexadécimal"""
        h = self.hash(code)
        return ''.join(hex(self.char_to_num[c])[2:].zfill(2) for c in h)
