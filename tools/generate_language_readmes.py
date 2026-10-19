#!/usr/bin/env python3
"""Generate `langs/<Language>/README.md` for every implementation folder.

The per-language READMEs are generated rather than hand-written so they cannot
drift from the code: the ciphertext table comes from `tests/reference.py`, and the
commands match what `tests/run_tests.py` actually runs.

    python tools/generate_language_readmes.py           # write the files
    python tools/generate_language_readmes.py --check   # fail if any is stale
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))
import reference  # noqa: E402

OPENSSL_INSTALL = """\
* **Debian / Ubuntu**: `sudo apt install build-essential libssl-dev`
* **macOS**: `brew install openssl`
* **Windows**: install OpenSSL (or Strawberry Perl, which ships the headers,
  import libraries and DLLs). The test suite finds it automatically and honours
  an `OPENSSL_DIR` override."""

LANGUAGES: list[dict] = [
    {
        "folder": "C",
        "name": "C",
        "ext": ".c",
        "category": "Systems",
        "library": "OpenSSL EVP (`EVP_aes_<bits>_cbc`)",
        "blurb": "AES in CBC mode through the OpenSSL EVP API, using the library's own PKCS#7 padding.",
        "install": OPENSSL_INSTALL,
        "build": "gcc -o rijndael-{bits} langs/C/{bits}bit/Rijndael.c -lssl -lcrypto",
        "run": "./rijndael-{bits}",
        "skills": [
            "Calling the OpenSSL EVP API (`EVP_EncryptInit_ex`, `EVP_EncryptUpdate`, `EVP_EncryptFinal_ex`)",
            "Deriving a deterministic key and IV instead of random bytes",
            "Formatting ciphertext as lowercase hex with `printf`",
        ],
        "filter": "c-",
    },
    {
        "folder": "C++",
        "name": "C++",
        "ext": ".cpp",
        "category": "Systems",
        "library": "OpenSSL EVP (`EVP_aes_<bits>_cbc`)",
        "blurb": "AES in CBC mode through the OpenSSL EVP API, wrapped in `std::vector` and `<iostream>` formatting.",
        "install": OPENSSL_INSTALL,
        "build": "g++ -std=c++17 -o rijndael-{bits} langs/C++/{bits}bit/Rijndael.cpp -lssl -lcrypto",
        "run": "./rijndael-{bits}",
        "skills": [
            "Calling the OpenSSL EVP API from C++ with `nullptr` and `std::vector` buffers",
            "Formatting hex with `<iomanip>` (`std::setw`, `std::setfill`)",
            "Keeping the key, IV and plaintext in a small anonymous namespace",
        ],
        "filter": "cpp-",
    },
    {
        "folder": "C#",
        "name": "C#",
        "ext": ".cs",
        "category": ".NET",
        "library": "`System.Security.Cryptography.Aes`",
        "blurb": "AES in CBC mode with `Aes.Create()`, `CipherMode.CBC` and `PaddingMode.PKCS7`.",
        "install": """\
* **Windows**: `winget install Microsoft.DotNet.SDK.8`
* **macOS**: `brew install dotnet`
* **Debian / Ubuntu**: `sudo apt install dotnet-sdk-8.0`""",
        "build": """\
dotnet new console -o build/csharp-{bits}
cp langs/C#/{bits}bit/Rijndael.cs build/csharp-{bits}/Program.cs""",
        "run": "dotnet run --project build/csharp-{bits}",
        "skills": [
            "Configuring `Aes` explicitly (`KeySize`, `CipherMode.CBC`, `PaddingMode.PKCS7`)",
            "Driving an `ICryptoTransform` from `aes.CreateEncryptor()` over the plaintext bytes",
            "Converting bytes with `Convert.ToHexString` and `Encoding.UTF8`",
        ],
        "filter": "csharp-",
    },
    {
        "folder": "Haskell",
        "name": "Haskell",
        "ext": ".hs",
        "category": "Functional",
        "library": "cryptonite (`Crypto.Cipher.AES`)",
        "blurb": "AES in CBC mode with cryptonite, padding the plaintext with a hand-written PKCS#7 helper.",
        "install": """\
* Install GHC 9.x, then the cipher library:
  ```sh
  cabal update
  cabal install --lib cryptonite
  ```""",
        "build": "ghc -package cryptonite -package memory -package bytestring -package base \\\n    langs/Haskell/{bits}bit/Rijndael.hs -o rijndael-{bits}",
        "run": "./rijndael-{bits}",
        "skills": [
            "Typed block ciphers: `cipherInit` into a `CryptoFailable`",
            "`cbcEncrypt` with a `Maybe (IV c)` from `makeIV`",
            "Encoding bytes to hex with `convertToBase Base16` from the `memory` package",
        ],
        "filter": "haskell-",
    },
    {
        "folder": "Java",
        "name": "Java",
        "ext": ".java",
        "category": "JVM",
        "library": "JCA (`javax.crypto.Cipher`)",
        "blurb": "AES in CBC mode through the Java Cryptography Architecture, using `AES/CBC/PKCS5Padding`.",
        "install": """\
* Any JDK 17 or newer (`javac` and `java` on the `PATH`):
  `sudo apt install openjdk-21-jdk`, `brew install openjdk`, or
  `winget install Microsoft.OpenJDK.21`""",
        "build": "javac -d build/java-{bits} langs/Java/{bits}bit/Rijndael.java",
        "run": "java -cp build/java-{bits} Rijndael",
        "skills": [
            "`Cipher.getInstance(\"AES/CBC/PKCS5Padding\")` with a `SecretKeySpec` and `IvParameterSpec`",
            "PKCS#5 padding is PKCS#7 for a 16-byte block, which is why the ciphertext matches the other languages",
            "Formatting bytes as lowercase hex with `String.format(\"%02x\", ...)`",
        ],
        "filter": "java-",
    },
    {
        "folder": "JavaScript",
        "name": "JavaScript",
        "ext": ".js",
        "category": "Web",
        "library": "Node.js `node:crypto`",
        "blurb": "AES in CBC mode with Node's built-in `createCipheriv`, which pads with PKCS#7 automatically.",
        "install": """\
* Node.js 20 or newer (`node --version`). The example is an ES module, which is
  why it imports from `node:crypto` and runs as-is under this repository's
  `\"type\": \"module\"` package manifest.""",
        "build": "# nothing to build",
        "run": "node langs/JavaScript/{bits}bit/Rijndael.js",
        "skills": [
            "`createCipheriv('aes-<bits>-cbc', key, iv)` and the streaming `update`/`final` pair",
            "Building deterministic `Buffer`s with `Array.from({ length }, (_, i) => i)`",
            "Hex output with `Buffer.toString('hex')`",
        ],
        "filter": "javascript-",
    },
    {
        "folder": "Kotlin",
        "name": "Kotlin",
        "ext": ".kt",
        "category": "JVM",
        "library": "JCA (`javax.crypto.Cipher`)",
        "blurb": "AES in CBC mode through the Java Cryptography Architecture, written as a single Kotlin file.",
        "install": """\
* A JDK 17 or newer plus the Kotlin compiler (`kotlinc -version`):
  `brew install kotlin`, `sdk install kotlin`, or `winget install Kotlin.Kotlin`""",
        "build": "kotlinc langs/Kotlin/{bits}bit/Rijndael.kt -include-runtime -d rijndael-{bits}.jar",
        "run": "java -jar rijndael-{bits}.jar",
        "skills": [
            "`Cipher.getInstance(\"AES/CBC/PKCS5Padding\")` with `SecretKeySpec` and `IvParameterSpec`",
            "Building key/IV bytes with `ByteArray(n) { index -> index.toByte() }`",
            "Hex output with `joinToString` and `\"%02x\".format(byte)`",
        ],
        "filter": "kotlin-",
    },
    {
        "folder": "PHP",
        "name": "PHP",
        "ext": ".php",
        "category": "Scripting",
        "library": "OpenSSL (`openssl_encrypt`)",
        "blurb": "AES in CBC mode with `openssl_encrypt` and `OPENSSL_RAW_DATA`, so the raw ciphertext can be hex-encoded.",
        "install": """\
* PHP 8 with the **openssl** extension (usually compiled in; on Windows uncomment
  `extension=openssl` in `php.ini`). The test suite passes `-d extension=openssl`
  so it works either way.""",
        "build": "# nothing to build",
        "run": "php -d extension=openssl langs/PHP/{bits}bit/Rijndael.php",
        "skills": [
            "`openssl_encrypt(..., 'aes-<bits>-cbc', $key, OPENSSL_RAW_DATA, $iv)`",
            "Building binary strings with `implode('', array_map('chr', range(0, $n - 1)))`",
            "Hex output with `bin2hex`",
        ],
        "filter": "php-",
    },
    {
        "folder": "Python",
        "name": "Python",
        "ext": ".py",
        "category": "Scripting",
        "library": "PyCryptodome (`Crypto.Cipher.AES`)",
        "blurb": "AES in CBC mode with PyCryptodome, padding through `Crypto.Util.Padding`.",
        "install": """\
* Python 3 and the cipher libraries:
  ```sh
  pip install pycryptodome cryptography
  ```""",
        "build": "# nothing to build",
        "run": "python langs/Python/{bits}bit/Rijndael.py",
        "skills": [
            "`AES.new(key, AES.MODE_CBC, iv)` plus `pad(..., AES.block_size)`",
            "Building deterministic bytes with `bytes(range(n))`",
            "Hex output with `bytes.hex()`",
        ],
        "filter": "python",
        "extra": """\
`rijndael.py` in this folder is the extra 256-bit example built on the
`cryptography` package instead of PyCryptodome. It prints the same lines as
`256bit/Rijndael.py`, and the suite runs it as the `python-cryptography` case:

```sh
python langs/Python/rijndael.py
```""",
    },
    {
        "folder": "Ruby",
        "name": "Ruby",
        "ext": ".rb",
        "category": "Scripting",
        "library": "OpenSSL (`OpenSSL::Cipher`)",
        "blurb": "AES in CBC mode with Ruby's bundled OpenSSL bindings.",
        "install": """\
* Ruby 3.x with OpenSSL support, which the standard installers ship
  (`ruby -ropenssl -e "puts OpenSSL::OPENSSL_VERSION"`).""",
        "build": "# nothing to build",
        "run": "ruby langs/Ruby/{bits}bit/Rijndael.rb",
        "skills": [
            "`OpenSSL::Cipher.new('aes-<bits>-cbc')` with `encrypt`, `key=` and `iv=`",
            "Building binary strings with `(0...n).map(&:chr).join`",
            "Hex output with `unpack1('H*')`",
        ],
        "filter": "ruby-",
    },
    {
        "folder": "TypeScript",
        "name": "TypeScript",
        "ext": ".ts",
        "category": "Web",
        "library": "Node.js `node:crypto`",
        "blurb": "AES in CBC mode with Node's `createCipheriv`, typed and compiled with the project's own TypeScript.",
        "install": """\
* Node.js 20 or newer, then the repository's dev dependencies (TypeScript and
  `@types/node`):
  ```sh
  npm install
  ```""",
        "build": "npx tsc langs/TypeScript/{bits}bit/Rijndael.ts \\\n    --outDir build/ts-{bits} --module nodenext --moduleResolution nodenext \\\n    --target ES2022 --types node --skipLibCheck",
        "run": "node build/ts-{bits}/Rijndael.js",
        "skills": [
            "`createCipheriv('aes-<bits>-cbc', key, iv)` from `node:crypto`",
            "Typed `Buffer` helpers and `import` syntax compiled to ESM",
            "Hex output with `Buffer.toString('hex')`",
        ],
        "filter": "typescript-",
    },
]

# Extra line for the compiled/one-artifact languages, where the "run" step depends
# on a file the build produced.
RUN_NOTES = {
    "C": "On Windows the binary is `rijndael-{bits}.exe`.",
    "C++": "On Windows the binary is `rijndael-{bits}.exe`.",
    "Haskell": "On Windows the binary is `rijndael-{bits}.exe`.",
    "Kotlin": "The build step writes `rijndael-{bits}.jar` in the repository root.",
}

PROTOCOL_BLOCK = """\
```text
AES-<bits>-CBC
KEY=<lowercase hex, bits/8 bytes: 00 01 02 ...>
IV=<lowercase hex, 16 bytes: 00 01 ... 0f>
PLAINTEXT={plaintext}
CIPHERTEXT=<lowercase hex>
```"""


def render(language: dict) -> str:
    """The full markdown of one language folder's README."""
    smallest = reference.KEY_SIZES[0]
    rows = "\n".join(
        f"| {bits}-bit | `{reference.ciphertext_for(bits).hex()}` |"
        for bits in reference.KEY_SIZES
    )
    skills = "\n".join(f"- {item}" for item in language["skills"])
    files = ", ".join(f"`{bits}bit/Rijndael{language['ext']}`" for bits in reference.KEY_SIZES)
    build = language["build"].format(bits=smallest)
    run = language["run"].format(bits=smallest)

    sections = [
        f"# {language['name']} — Rijndael/AES examples",
        "",
        language["blurb"],
        "",
        "| | |",
        "| --- | --- |",
        f"| Language | {language['name']} (`{language['ext']}`) |",
        f"| Category | {language['category']} |",
        f"| Cryptography | {language['library']} |",
        f"| Implementations | {files} |",
        f"| Verified by | `python tests/run_tests.py --filter {language['filter']}` |",
        "",
        "## The shared protocol",
        "",
        "Every implementation in this repository prints the same five lines for its key",
        "size, so the ciphertext matches in every language — see the",
        "[root README](../../README.md#shared-console-protocol):",
        "",
        PROTOCOL_BLOCK.format(plaintext=reference.PLAINTEXT),
        "",
        "The key and IV are derived from their byte index (never random) and AES runs in",
        "CBC mode with PKCS#7 padding, which is what makes the output comparable.",
        "",
        "## Expected output",
        "",
        "The ciphertext this language prints for each key size, checked against",
        "[`tests/expected`](../../tests/expected):",
        "",
        "| Key size | Ciphertext |",
        "| --- | --- |",
        rows,
        "",
        "## Toolchain",
        "",
        language["install"],
        "",
        "## Build and run",
        "",
        f"From the repository root, for the {smallest}-bit example:",
        "",
        "```sh",
        build,
        run,
        "```",
        "",
        f"Swap `{smallest}bit` for `192bit` or `256bit` (and the matching key size in the",
        "command) for the other two examples.",
    ]

    note = RUN_NOTES.get(language["name"])
    if note:
        sections += ["", note.format(bits=smallest)]

    sections += ["", "## What it demonstrates", "", skills]

    if language.get("extra"):
        sections += ["", "## Extra example", "", language["extra"]]

    sections += [
        "",
        "## Adding or changing this language",
        "",
        "The implementations, this README and the test case are generated from the same",
        "facts: update `LANGUAGES` in `tools/generate_language_readmes.py` (documentation),",
        "`LANGUAGES` in `tests/run_tests.py` (the suite) and `LANGUAGES` in",
        "`tools/generate-data.mjs` (the dashboard), then run:",
        "",
        "```sh",
        "python tools/generate_language_readmes.py",
        "python tests/run_tests.py",
        "```",
        "",
    ]

    return "\n".join(sections)


def main() -> int:
    check = "--check" in sys.argv[1:]
    stale: list[Path] = []

    for language in LANGUAGES:
        path = ROOT / "langs" / language["folder"] / "README.md"
        text = render(language)
        if check:
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != text:
                stale.append(path)
        else:
            path.write_text(text, encoding="utf-8", newline="\n")
            print("wrote", path.relative_to(ROOT))

    if check:
        if stale:
            print("stale — run `python tools/generate_language_readmes.py`:")
            for path in stale:
                print(" -", path.relative_to(ROOT))
            return 1
        print(f"{len(LANGUAGES)} per-language READMEs are up to date")

    return 0


if __name__ == "__main__":
    sys.exit(main())
