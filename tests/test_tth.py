"""
test_tth.py
Tests unitaires pour le Toy Tetragraph Hash
"""

import sys
import os

# Ajouter le dossier parent au chemin pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.crypto.tth_hash import ToyTetragraphHash, get_tth, compute_fingerprint


class TestToyTetragraphHash:
    """Tests pour la classe ToyTetragraphHash"""
    
    def setup_method(self):
        """Initialisation avant chaque test"""
        self.tth = ToyTetragraphHash()
    
    def test_code_conversion(self):
        """Test de conversion code ↔ nombres"""
        code = "AF15GH25"
        numbers = self.tth._code_to_numbers(code)
        assert len(numbers) == 8
        assert self.tth._numbers_to_code(numbers) == code
    
    def test_hash_length(self):
        """Test que le hash fait toujours 4 caractères"""
        test_cases = [
            "AF15GH25",
            "123456789012",
            "HELLO",
            "A1B2C3D4E5F6",
            "",
        ]
        
        for code in test_cases:
            h = self.tth.hash(code)
            assert len(h) == 4, f"Hash de '{code}' doit faire 4 caractères"
            for c in h:
                assert c in self.tth.alphabet
    
    def test_deterministic(self):
        """Test que le hash est déterministe"""
        code = "AF15GH25"
        h1 = self.tth.hash(code)
        h2 = self.tth.hash(code)
        assert h1 == h2
    
    def test_avalanche_effect(self):
        """Test de l'effet avalanche"""
        code1 = "AF15GH25"
        code2 = "AF15GH26"  # Un seul caractère change
        
        h1 = self.tth.hash(code1)
        h2 = self.tth.hash(code2)
        
        # En bonne fonction de hash, les résultats doivent être différents
        assert h1 != h2, "Un changement d'un caractère doit changer le hash"
    
    def test_different_codes_different_hashes(self):
        """Test que des codes différents donnent des hashes différents"""
        codes = [
            "AF15GH25",
            "BF15GH25",
            "AF15GH26",
            "AF15GH25 ",
        ]
        
        hashes = set()
        for code in codes:
            h = self.tth.hash(code)
            hashes.add(h)
        
        assert len(hashes) == len(codes)
    
    def test_verify_function(self):
        """Test de la fonction de vérification"""
        code = "AF15GH25"
        fingerprint = self.tth.hash(code)
        
        assert self.tth.verify(code, fingerprint) is True
        assert self.tth.verify(code, "AAAA") is False
        assert self.tth.verify("WRONGCODE", fingerprint) is False
    
    def test_empty_code(self):
        """Test du code vide"""
        assert self.tth.hash("") == "AAAA"
        assert self.tth.hash("   ") == "AAAA"
    
    def test_invalid_characters(self):
        """Test des caractères invalides"""
        import pytest
        with pytest.raises(ValueError):
            self.tth.hash("HELLO@123")


class TestTTHIntegration:
    """Tests d'intégration avec le protocole de vote"""
    
    def setup_method(self):
        self.tth = get_tth()
    
    def test_compute_fingerprint(self):
        """Test de la fonction compute_fingerprint"""
        N2 = "4K89LM726WX1"
        fingerprint = compute_fingerprint(N2)
        
        assert len(fingerprint) == 4
        # Le même code doit donner la même empreinte
        assert fingerprint == compute_fingerprint(N2)
    
    def test_commissioner_use_case(self):
        """Cas d'usage: le commissaire vérifie un vote"""
        
        # Codes secrets des votants
        voters_N2 = [
            "4K89LM726WX1",
            "3F12AB459CD2",
            "7H56QR981ZV3",
        ]
        
        # Le commissaire reçoit seulement les empreintes
        fingerprints = {compute_fingerprint(N2) for N2 in voters_N2}
        
        # Pendant le vote, le commissaire reçoit un bulletin
        bulletin_fingerprint = compute_fingerprint(voters_N2[0])
        
        # Vérification
        assert bulletin_fingerprint in fingerprints
        
        # Un N2 frauduleux est rejeté
        fake_fingerprint = compute_fingerprint("ZZ99ZZ99ZZ99")
        assert fake_fingerprint not in fingerprints


def run_all_tests():
    """Exécute tous les tests"""
    print("=" * 60)
    print("TESTS UNITAIRES - TOY TETRAGRAPH HASH")
    print("=" * 60)
    
    test_class = TestToyTetragraphHash()
    test_class.setup_method()
    
    tests = [
        ("Conversion code ↔ nombres", test_class.test_code_conversion),
        ("Longueur du hash (4 caractères)", test_class.test_hash_length),
        ("Déterminisme", test_class.test_deterministic),
        ("Effet avalanche", test_class.test_avalanche_effect),
        ("Codes différents → hashes différents", test_class.test_different_codes_different_hashes),
        ("Fonction de vérification", test_class.test_verify_function),
        ("Code vide", test_class.test_empty_code),
    ]
    
    passed = 0
    failed = 0
    
    for name, test in tests:
        try:
            test()
            print(f"✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {name}")
            print(f"  → {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {name}")
            print(f"  → Erreur: {e}")
            failed += 1
    
    print("\n" + "-" * 40)
    print(f"Résultats: {passed} réussis, {failed} échoués")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)