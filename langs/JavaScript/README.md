# JavaScript — Rijndael/AES examples

AES in CBC mode with Node's built-in `createCipheriv`, which pads with PKCS#7 automatically.

| | |
| --- | --- |
| Language | JavaScript (`.js`) |
| Category | Web |
| Cryptography | Node.js `node:crypto` |
| Implementations | `128bit/Rijndael.js`, `192bit/Rijndael.js`, `256bit/Rijndael.js` |
| Verified by | `python tests/run_tests.py --filter javascript-` |

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

* Node.js 20 or newer (`node --version`). The example is an ES module, which is
  why it imports from `node:crypto` and runs as-is under this repository's
  `"type": "module"` package manifest.

## Build and run

From the repository root, for the 128-bit example:

```sh
# nothing to build
node langs/JavaScript/128bit/Rijndael.js
```

Swap `128bit` for `192bit` or `256bit` (and the matching key size in the
command) for the other two examples.

## What it demonstrates

- `createCipheriv('aes-<bits>-cbc', key, iv)` and the streaming `update`/`final` pair
- Building deterministic `Buffer`s with `Array.from({ length }, (_, i) => i)`
- Hex output with `Buffer.toString('hex')`

## Adding or changing this language

The implementations, this README and the test case are generated from the same
facts: update `LANGUAGES` in `tools/generate_language_readmes.py` (documentation),
`LANGUAGES` in `tests/run_tests.py` (the suite) and `LANGUAGES` in
`tools/generate-data.mjs` (the dashboard), then run:

```sh
python tools/generate_language_readmes.py
python tests/run_tests.py
```
