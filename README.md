# Rijndael Encryption by Patrick Goodwin

Some of my Rijndael encryption examples in many different programming languages. All are available in 128, 192, and 256 bit examples.

## Showcase dashboard

`src/` is a Vue 3 + TypeScript app built by Vite: a fully client-side dashboard
(no backend, no live compilers) with a sidebar of every implementation and a main
panel whose tabs are **Source Code**, **Overview** and **Console Output**. It also
has a language search box, and Category and Key size filters.

Every language has its own address — `/c`, `/csharp`, `/python` — and the key size
is part of it too: `/c/128`, `/csharp/256`, `/csharp/256/overview`,
`/python-cryptography/256`. The sidebar entries are real links, so they can be
copied, bookmarked or opened in a new tab, and the address bar follows the header's
key-size dropdown. The site root opens C at 128 bits, the reference walkthrough
(`DEFAULT_LANG_ID` in `src/store/data.ts`). The older one-segment addresses
(`/c-128`, `/csharp-256/overview`) still work and are canonicalised on load.

```sh
npm install        # once
npm start          # regenerate the data, then serve the dashboard on :5173
npm run build      # regenerate the data, type-check, and write dist/
npm run preview    # serve the built dist/
npm run data       # only regenerate public/encryption-data.js
npm run typecheck  # vue-tsc --noEmit
```

Every implementation lives under `langs/`, as
`langs/<Language>/<bits>bit/Rijndael<ext>` plus the standalone
`langs/Python/rijndael.py`. `tools/generate-data.mjs` reads those real files,
records each one's mode and library, and writes `public/encryption-data.js`.
`npm start` and `npm run build` run it first, so a new implementation shows up
without editing the app. Every generated entry links back to its exact folder on
GitHub (`langs/C#` is URL-encoded as `langs/C%23`).

The published site lives at **<https://encryption.pattygcoding.com/>**. Every
address it answers on — each language, key size and tab — is listed in
[`docs/links.md`](docs/links.md), with the same list as one URL per line in
[`docs/links.txt`](docs/links.txt):

```sh
python tools/generate_link_index.py          # write both files
python tools/generate_link_index.py --check  # fail if either is stale
```

## Shared console protocol

Every implementation prints the same five lines for its key size, so the same
ciphertext comes out of every language. The protocol is defined once in
`tests/reference.py`:

```
AES-<bits>-CBC
KEY=<lowercase hex, bits/8 bytes: 00 01 02 ...>
IV=<lowercase hex, 16 bytes: 00 01 ... 0f>
PLAINTEXT=The quick brown fox jumps over the lazy dog.
CIPHERTEXT=<lowercase hex>
```

* AES in **CBC** mode with **PKCS#7** padding (Java/Kotlin name it
  `AES/CBC/PKCS5Padding`, which is the same padding for a 16-byte block).
* The key and IV are fixed and derived from their index, never random, so the
  output is deterministic and comparable byte for byte.
* Hex is lowercase and the newline is `\n`; the suite normalises CRLF, so a
  Windows console is fine.

For example, `tests/expected/aes-128.txt` is:

```
AES-128-CBC
KEY=000102030405060708090a0b0c0d0e0f
IV=000102030405060708090a0b0c0d0e0f
PLAINTEXT=The quick brown fox jumps over the lazy dog.
CIPHERTEXT=d5f239401cf82914474428e33d8b1c9e380a8f51f8800d23a97775715faf4ba9797190e589891683f9ddd0917270b0f5
```

## Tests

`tests/run_tests.py` compiles and runs all 34 implementations and compares each
one's output with `tests/expected/aes-<bits>.txt`:

```sh
python tests/run_tests.py                # everything
python tests/run_tests.py --filter java  # only matching cases
python tests/run_tests.py --list         # show the cases without running them
python tests/run_tests.py --update       # regenerate tests/expected from reference.py
```

A toolchain that is not installed is reported as **SKIP** rather than a failure, so
the suite is usable with a partial setup. To run everything you need:

| Implementation | Needs |
| --- | --- |
| C, C++ | a C/C++ compiler and OpenSSL development files (`libssl-dev`, `brew install openssl`, or OpenSSL for Windows; `OPENSSL_DIR` overrides detection) |
| C# | .NET SDK 8+ |
| Haskell | GHC plus `cabal install --lib cryptonite` |
| Java, Kotlin | JDK 17+ and the Kotlin compiler |
| JavaScript, TypeScript | Node 20+ (TypeScript comes from `npm install`) |
| PHP | the `openssl` extension (the suite passes `-d extension=openssl`) |
| Python | `pip install pycryptodome cryptography` |
| Ruby | Ruby with OpenSSL support (standard) |

Build output goes to `tests/build/`, which is ignored by git. Add a language by
writing `langs/<Language>/<bits>bit/Rijndael<ext>` to the protocol above, adding it
to `LANGUAGES` in `tests/run_tests.py` (the suite), `tools/generate-data.mjs` (the
dashboard) and `tools/generate_language_readmes.py` (its README), then running:

```sh
python tools/generate_language_readmes.py
python tests/run_tests.py
npm run data
```

## Language folders

Every folder under `langs/` carries its own `README.md`: the implementation's
library, the shared protocol, the ciphertext it must produce, how to install the
toolchain on Debian/macOS/Windows, the exact build and run commands, what it
demonstrates, and the `--filter` that runs just that language:

* [`langs/C/README.md`](langs/C/README.md), [`langs/C++/README.md`](langs/C++/README.md),
  [`langs/C#/README.md`](langs/C%23/README.md)
* [`langs/Haskell/README.md`](langs/Haskell/README.md), [`langs/Java/README.md`](langs/Java/README.md),
  [`langs/JavaScript/README.md`](langs/JavaScript/README.md)
* [`langs/Kotlin/README.md`](langs/Kotlin/README.md), [`langs/PHP/README.md`](langs/PHP/README.md),
  [`langs/Python/README.md`](langs/Python/README.md)
* [`langs/Ruby/README.md`](langs/Ruby/README.md), [`langs/TypeScript/README.md`](langs/TypeScript/README.md)

They are generated from the same facts as the suite, so they cannot drift from
the code:

```sh
python tools/generate_language_readmes.py          # write them
python tools/generate_language_readmes.py --check  # fail if any is stale
```

### Deploying to GitHub Pages

`.github/workflows/deploy.yml` runs on every push to `main`: it installs Node 22,
runs `npm ci` and `npm run build`, uploads `dist/` as the Pages artifact and
publishes it. Pages must be set to publish from **GitHub Actions** (not from a
branch), and the custom domain is a repository setting:

```sh
gh api -X POST repos/pattygcoding/Rijndael-Encryption/pages -f build_type=workflow
gh api -X PUT repos/pattygcoding/Rijndael-Encryption/pages \
    -f cname=encryption.pattygcoding.com
```

The DNS side is a single record at the domain's provider:

```
encryption   CNAME   pattygcoding.github.io
```

If the provider proxies traffic (Cloudflare does by default), switch that record
to **DNS only** (grey cloud); a proxied record breaks Pages' certificate checks.

Pages has no rewrite rules, so the tracked `public/404.html` stands in for them:
it is served for any path it cannot find and rebuilds the request as
`index.html?lang=<id>&tab=<tab>`, so `/csharp-256` and `/csharp-256/overview`
work when opened directly. The dashboard then puts the pretty path back with the
History API. The app derives its deployment prefix at load (`APP_DIR` in
`src/store/session.ts`), so the same build also works under a
`<user>.github.io/<repo>/` path.
