# C — Rijndael/AES examples

AES in CBC mode through the OpenSSL EVP API, using the library's own PKCS#7 padding.

| | |
| --- | --- |
| Language | C (`.c`) |
| Category | Systems |
| Cryptography | OpenSSL EVP (`EVP_aes_<bits>_cbc`) |
| Implementations | `128bit/Rijndael.c`, `192bit/Rijndael.c`, `256bit/Rijndael.c` |
| Verified by | `python tests/run_tests.py --filter c-` |

## The shared protocol

Every implementation in this repository prints the same five lines for its key
size, so the ciphertext matches in every language — see the
[root README](../../README.md#shared-console-protocol):

```text
AES-<bits>-CBC
KEY=<lowercase hex, bits/8 bytes: 00 01 02 ...>
IV=<lowercase hex, 16 bytes: 00 01 ... 0f>
PLAINTEXT=The quick brown fox jumps over the lazy dog.
CIPHERTEXT=<lowercase hex>
```

The key and IV are derived from their byte index (never random) and AES runs in
CBC mode with PKCS#7 padding, which is what makes the output comparable.

## Expected output

The ciphertext this language prints for each key size, checked against
[`tests/expected`](../../tests/expected):

| Key size | Ciphertext |
| --- | --- |
| 128-bit | `d5f239401cf82914474428e33d8b1c9e380a8f51f8800d23a97775715faf4ba9797190e589891683f9ddd0917270b0f5` |
| 192-bit | `10acab422ae42b3528294371bdbbc03761516108d758216e7c8b8f8049cc9c080336018902b511c82e9e8b1b993b2067` |
| 256-bit | `4846f83aa211e239aa62a21f527f089ee9ddbead30ee15d4e79b607a621b97bedb9b6f00a9b21f1b43a50b4c1be0edf2` |

## Toolchain

* **Debian / Ubuntu**: `sudo apt install build-essential libssl-dev`
* **macOS**: `brew install openssl`
* **Windows**: install OpenSSL (or Strawberry Perl, which ships the headers,
  import libraries and DLLs). The test suite finds it automatically and honours
  an `OPENSSL_DIR` override.

## Build and run

From the repository root, for the 128-bit example:

```sh
gcc -o rijndael-128 langs/C/128bit/Rijndael.c -lssl -lcrypto
./rijndael-128
```

Swap `128bit` for `192bit` or `256bit` (and the matching key size in the
command) for the other two examples.

On Windows the binary is `rijndael-128.exe`.

## What it demonstrates

- Calling the OpenSSL EVP API (`EVP_EncryptInit_ex`, `EVP_EncryptUpdate`, `EVP_EncryptFinal_ex`)
- Deriving a deterministic key and IV instead of random bytes
- Formatting ciphertext as lowercase hex with `printf`

## Adding or changing this language

The implementations, this README and the test case are generated from the same
facts: update `LANGUAGES` in `tools/generate_language_readmes.py` (documentation),
`LANGUAGES` in `tests/run_tests.py` (the suite) and `LANGUAGES` in
`tools/generate-data.mjs` (the dashboard), then run:

```sh
python tools/generate_language_readmes.py
python tests/run_tests.py
```
