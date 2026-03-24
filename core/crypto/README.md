Blind Signature Module :
 This module implements a blind signature scheme using RSA.
 Steps: 
 1. The voter blinds the message using a random factor.
 2. The administrator signs the blinded message.
 3. The voter unblinds the signature.
 This ensures that the administrator signs the vote without knowing its content.
 Functions:
 blind_message()  - blind_sign()   - unblind_signature()  <br>

RSA: <br>    
RSA is an asymmetric algorithm using a public/private key pair, secured by the integer factorization problem — given n = p × q, recovering p and q is computationally infeasible.<br>
In a voting system it serves two roles:<br>
-Encryption — the voter's ballot is encrypted with the authority's public key (c = mᵉ mod n). Only the authority's private key can decrypt it (m = cᵈ mod n), ensuring ballot secrecy from submission to tallying.  <br>
-Digital signature — the voter signs their ballot with their own private key. Anyone can verify it with the voter's public key, confirming authenticity without linking identity to the vote content.
