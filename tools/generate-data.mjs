// Builds `public/encryption-data.js` from the real implementations in this
// repository: every `<Language>/<bits>bit/Rijndael<ext>` file becomes one entry,
// plus the standalone `Python/rijndael.py` example.  The Vue app reads the payload
// from `window.ENCRYPTION_DATA`, so the browser never fetches source files itself.
//
// Run with `npm run data`; `npm start` and `npm run build` do it automatically.

import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(fileURLToPath(new URL("..", import.meta.url)));
const KEY_SIZES = [128, 192, 256];

// Display metadata per language folder.  `id` is the address slug the dashboard
// uses (`/c-128`), and `prism` is the Prism grammar class used for highlighting.
const LANGUAGES = [
    { folder: "C", name: "C", id: "c", prism: "language-c", ext: ".c", category: "Systems", api: "OpenSSL EVP" },
    { folder: "C#", name: "C#", id: "csharp", prism: "language-csharp", ext: ".cs", category: ".NET", api: "System.Security.Cryptography" },
    { folder: "C++", name: "C++", id: "cpp", prism: "language-cpp", ext: ".cpp", category: "Systems", api: "OpenSSL EVP" },
    { folder: "Haskell", name: "Haskell", id: "haskell", prism: "language-haskell", ext: ".hs", category: "Functional", api: "cryptonite" },
    { folder: "Java", name: "Java", id: "java", prism: "language-java", ext: ".java", category: "JVM", api: "Java Cryptography Architecture" },
    { folder: "JavaScript", name: "JavaScript", id: "javascript", prism: "language-javascript", ext: ".js", category: "Web", api: "Node.js crypto" },
    { folder: "Kotlin", name: "Kotlin", id: "kotlin", prism: "language-kotlin", ext: ".kt", category: "JVM", api: "Java Cryptography Architecture" },
    { folder: "PHP", name: "PHP", id: "php", prism: "language-php", ext: ".php", category: "Scripting", api: "OpenSSL" },
    { folder: "Python", name: "Python", id: "python", prism: "language-python", ext: ".py", category: "Scripting", api: "PyCryptodome" },
    { folder: "Ruby", name: "Ruby", id: "ruby", prism: "language-ruby", ext: ".rb", category: "Scripting", api: "OpenSSL" },
    { folder: "TypeScript", name: "TypeScript", id: "typescript", prism: "language-typescript", ext: ".ts", category: "Web", api: "Node.js crypto" },
];

// The one implementation that is not organised by key size.
const EXTRAS = [
    {
        id: "python-cryptography",
        name: "Python (cryptography)",
        language: "Python",
        category: "Scripting",
        keySize: 256,
        prism: "language-python",
        api: "cryptography",
        file: "Python/rijndael.py",
        folder: "Python",
        fixedId: true,
    },
];

// The block cipher mode a file asks its library for, read from the call it makes.
function detectMode(code) {
    if (/MODE_GCM|aes-\d+-gcm|AES\/GCM/i.test(code)) {
        return "GCM";
    }
    if (/ctrCombine|MODE_CTR|aes-\d+-ctr|AES\/CTR/i.test(code)) {
        return "CTR";
    }
    if (/CBC/i.test(code)) {
        return "CBC";
    }
    return "Library default";
}

async function readImplementation(entry, keySize, file) {
    const absolute = path.join(ROOT, file);
    if (!existsSync(absolute)) {
        return null;
    }
    const code = (await readFile(absolute, "utf8")).replace(/\r\n/g, "\n");
    let mode = detectMode(code);
    if (mode === "Library default" && entry.name === "C#") {
        // Aes.Create() defaults to CBC when the source never names the mode.
        mode = "CBC (default)";
    }
    // The verified output every implementation of this key size prints, captured by
    // tests/run_tests.py.  A checkout that has not run the suite yet has none, and
    // the Console Output tab then says so.
    const expectedFile = path.join(ROOT, "tests", "expected", `aes-${keySize}.txt`);
    const output = existsSync(expectedFile)
        ? (await readFile(expectedFile, "utf8")).replace(/\r\n/g, "\n").trimEnd()
        : "";
    return {
        id: entry.fixedId ? entry.id : `${entry.id}-${keySize}`,
        name: entry.name,
        language: entry.language ?? entry.name,
        category: entry.category,
        keySize,
        prism: entry.prism,
        api: entry.api,
        mode,
        file,
        folder: entry.fixedId ? entry.folder : `${entry.folder}/${keySize}bit`,
        output,
        code,
    };
}

function git(command, fallback) {
    try {
        const output = execFileSync("git", command, { cwd: ROOT, encoding: "utf8" }).trim();
        return output || fallback;
    } catch {
        return fallback;
    }
}

// `git@github.com:owner/repo.git` and `https://github.com/owner/repo.git` both
// become the browsable `https://github.com/owner/repo` the dashboard links to.
function repositoryUrl() {
    const remote = git(["config", "--get", "remote.origin.url"], "");
    if (remote) {
        const match = remote.match(/github\.com[:/]([^/]+\/[^/]+?)(?:\.git)?$/i);
        if (match) {
            return "https://github.com/" + match[1];
        }
    }
    if (process.env.GITHUB_REPOSITORY) {
        return "https://github.com/" + process.env.GITHUB_REPOSITORY;
    }
    return "https://github.com/pattygcoding/Rijndael-Encryption";
}

async function main() {
    const implementations = [];

    for (const language of LANGUAGES) {
        for (const keySize of KEY_SIZES) {
            const file = `${language.folder}/${keySize}bit/Rijndael${language.ext}`;
            const item = await readImplementation(language, keySize, file);
            if (item) {
                implementations.push(item);
            }
        }
    }

    for (const extra of EXTRAS) {
        const item = await readImplementation(extra, extra.keySize, extra.file);
        if (item) {
            implementations.push(item);
        }
    }

    const languageNames = [];
    for (const item of implementations) {
        if (!languageNames.includes(item.language)) {
            languageNames.push(item.language);
        }
    }

    const languageExtensions = {};
    for (const language of LANGUAGES) {
        languageExtensions[language.name] = language.ext;
    }

    const data = {
        meta: {
            updated: new Date().toISOString().slice(0, 10),
            implementationCount: implementations.length,
            languageCount: languageNames.length,
            repository: repositoryUrl(),
            branch: git(["rev-parse", "--abbrev-ref", "HEAD"], "main"),
        },
        keySizes: KEY_SIZES,
        implementations,
        languageExtensions,
    };

    const payload =
        "// Generated by tools/generate-data.mjs - do not edit by hand.\n" +
        "window.ENCRYPTION_DATA = " +
        JSON.stringify(data, null, 2) +
        ";\n";

    await mkdir(path.join(ROOT, "public"), { recursive: true });
    await writeFile(path.join(ROOT, "public", "encryption-data.js"), payload, "utf8");
    console.log(
        "encryption-data.js: " +
            implementations.length +
            " implementations across " +
            languageNames.length +
            " languages",
    );
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
