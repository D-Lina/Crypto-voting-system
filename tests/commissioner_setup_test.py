from core.entities.commissioner import Commissioner

def test_setup():
    commissioner = Commissioner()
    n1_codes = {"code1", "code2", "code3"}
    n2_fingerprints = {"fp1", "fp2"}
    
    commissioner.setup(n1_codes, n2_fingerprints)
    
    assert commissioner._valid_n1 == n1_codes
    assert commissioner._valid_n2_fingerprints == n2_fingerprints
    print("✅ Setup test passed!")

if __name__ == "__main__":
    test_setup()