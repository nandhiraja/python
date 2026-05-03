import ecdsa
import hashlib

class Wallet:
    def __init__(self, private_key=None):
        if private_key:
            self.private_key = private_key
        else:
            self.private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        self.public_key = self.private_key.get_verifying_key()
        
    @property
    def address(self):
        # We will simulate the address as 0x + first 4 chars + ... + last 4 chars of the public key hex for aesthetics.
        pub_hex = self.public_key.to_string().hex()
        return f"0x{pub_hex[:4]}...{pub_hex[-4:]}"

    def sign(self, data: str) -> str:
        signature = self.private_key.sign(data.encode('utf-8'), hashfunc=hashlib.sha256)
        return signature.hex()

def verify_signature(public_key_hex: str, signature_hex: str, data: str) -> bool:
    try:
        vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=ecdsa.SECP256k1)
        return vk.verify(bytes.fromhex(signature_hex), data.encode('utf-8'), hashfunc=hashlib.sha256)
    except Exception:
        return False
