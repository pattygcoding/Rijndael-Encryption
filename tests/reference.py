"""The reference implementation of the shared encryption protocol.

Every language implementation must print exactly `output(bits)`.  The protocol is
deliberately simple so the ciphertext is deterministic and can be compared
byte-for-byte:

* AES in CBC mode with PKCS#7 padding.
* Plaintext: ``The quick brown fox jumps over the lazy dog.``
* Key: ``bits / 8`` bytes ``00 01 02 ...``
* IV: 16 bytes ``00 01 ... 0f``
* Output: five lowercase-hex lines (see ``output``).

Run ``python tests/run_tests.py --update`` to regenerate ``tests/expected`` from
this file.
"""

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

PLAINTEXT = "The quick brown fox jumps over the lazy dog."
IV = bytes(range(16))
KEY_SIZES = (128, 192, 256)


def key_for(bits: int) -> bytes:
    return bytes(range(bits // 8))


def ciphertext_for(bits: int) -> bytes:
    key = key_for(bits)
    return AES.new(key, AES.MODE_CBC, IV).encrypt(pad(PLAINTEXT.encode("utf-8"), AES.block_size))


def output(bits: int) -> str:
    key = key_for(bits)
    ciphertext = ciphertext_for(bits)
    return (
        f"AES-{bits}-CBC\n"
        f"KEY={key.hex()}\n"
        f"IV={IV.hex()}\n"
        f"PLAINTEXT={PLAINTEXT}\n"
        f"CIPHERTEXT={ciphertext.hex()}\n"
    )


if __name__ == "__main__":
    for size in KEY_SIZES:
        print(output(size), end="")
