from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, padding

def decrypt_and_display(encrypted_result, private_key):
    decrypted_result = private_key.decrypt(
        encrypted_result,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    print("The decrypted result is: ", int.from_bytes(decrypted_result, byteorder='big'))
