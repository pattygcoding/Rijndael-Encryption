# Java — Rijndael/AES examples

AES in CBC mode through the Java Cryptography Architecture, using `AES/CBC/PKCS5Padding`.

| | |
| --- | --- |
| Language | Java (`.java`) |
| Category | JVM |
| Cryptography | JCA (`javax.crypto.Cipher`) |
| Implementations | `128bit/Rijndael.java`, `192bit/Rijndael.java`, `256bit/Rijndael.java` |
| Verified by | `python tests/run_tests.py --filter java-` |

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

* Any JDK 17 or newer (`javac` and `java` on the `PATH`):
  `sudo apt install openjdk-21-jdk`, `brew install openjdk`, or
  `winget install Microsoft.OpenJDK.21`

## Build and run

From the repository root, for the 128-bit example:

```sh
javac -d build/java-128 langs/Java/128bit/Rijndael.java
java -cp build/java-128 Rijndael
```

Swap `128bit` for `192bit` or `256bit` (and the matching key size in the
command) for the other two examples.

## What it demonstrates

- `Cipher.getInstance("AES/CBC/PKCS5Padding")` with a `SecretKeySpec` and `IvParameterSpec`
- PKCS#5 padding is PKCS#7 for a 16-byte block, which is why the ciphertext matches the other languages
- Formatting bytes as lowercase hex with `String.format("%02x", ...)`

## Adding or changing this language

The implementations, this README and the test case are generated from the same
facts: update `LANGUAGES` in `tools/generate_language_readmes.py` (documentation),
`LANGUAGES` in `tests/run_tests.py` (the suite) and `LANGUAGES` in
`tools/generate-data.mjs` (the dashboard), then run:

```sh
python tools/generate_language_readmes.py
python tests/run_tests.py
```
