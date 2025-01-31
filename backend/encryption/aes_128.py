from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

# Function to convert user input key to a 16-byte (128-bit) AES key
def format_key(user_key):
    user_key = user_key.encode('utf-8')  # Ensure key is in byte format
    if len(user_key) < 16:
        return user_key.ljust(16, b'0')  # Pad with '0' bytes if too short
    elif len(user_key) > 16:
        return user_key[:16]  # Truncate if too long
    return user_key

def encrypt_aes_128(plaintext, key):
    try:
        # Generate a random initialization vector (IV)
        iv = os.urandom(16)  # AES block size is 16 bytes

        # Initialize cipher object with AES in CBC mode
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Pad the plaintext to a multiple of the block size (16 bytes)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()

        # Encrypt the padded data
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # Return the IV and ciphertext together (IV is needed for decryption)
        return iv + ciphertext

    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")

def decrypt_aes_128(ciphertext, key):
    try:
        # Extract the IV from the ciphertext
        iv = ciphertext[:16]
        actual_ciphertext = ciphertext[16:]

        # Initialize cipher object with AES in CBC mode
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the data
        padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()

        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        return plaintext.decode('utf-8')

    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")
