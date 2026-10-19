from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

KEY_BITS = 256
PLAINTEXT = b"The quick brown fox jumps over the lazy dog."


def main() -> None:
    key = bytes(range(KEY_BITS // 8))
    iv = bytes(range(16))
    ciphertext = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(PLAINTEXT, AES.block_size))

    print(f"AES-{KEY_BITS}-CBC")
    print(f"KEY={key.hex()}")
    print(f"IV={iv.hex()}")
    print(f"PLAINTEXT={PLAINTEXT.decode()}")
    print(f"CIPHERTEXT={ciphertext.hex()}")


if __name__ == "__main__":
    main()
