from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

KEY_BITS = 256
PLAINTEXT = b"The quick brown fox jumps over the lazy dog."


def main() -> None:
    key = bytes(range(KEY_BITS // 8))
    iv = bytes(range(16))

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded = padder.update(PLAINTEXT) + padder.finalize()

    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    print(f"AES-{KEY_BITS}-CBC")
    print(f"KEY={key.hex()}")
    print(f"IV={iv.hex()}")
    print(f"PLAINTEXT={PLAINTEXT.decode()}")
    print(f"CIPHERTEXT={ciphertext.hex()}")


if __name__ == "__main__":
    main()
