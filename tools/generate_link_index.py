#!/usr/bin/env python3
"""Generate `docs/links.md` and `docs/links.txt`: every address the showcase answers on.

    python tools/generate_link_index.py           # write both files
    python tools/generate_link_index.py --check   # fail if either is stale

The list is read from `langs/` through `tools/languages.py`, so adding a language or
a key size updates it (and the per-language READMEs) with no hand-editing.
"""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import languages  # noqa: E402

ROOT = languages.ROOT
DOCS = ROOT / "docs"
BASE = "https://encryption.pattygcoding.com"
REPO = "https://github.com/pattygcoding/Rijndael-Encryption"
BRANCH = "main"

# (address suffix, tab label) - the default tab carries no suffix.
TABS = [("", "Source Code"), ("/overview", "Overview"), ("/output", "Console Output")]


def url(language_id: str, bits: int | None = None, tab: str = "") -> str:
    """The address of one view: `/c`, `/c/256` or `/c/256/overview`."""
    if bits is None:
        return f"{BASE}/{language_id}"
    return f"{BASE}/{language_id}/{bits}{tab}"


def repo_url(path: str) -> str:
    # `C#` and `C++` need encoding in a link, so quote every path segment.
    encoded = "/".join(quote(segment, safe="") for segment in path.split("/"))
    return f"{REPO}/tree/{BRANCH}/{encoded}"


def all_urls() -> list[str]:
    """Every canonical address, in reading order: the root, then each language."""
    urls = [f"{BASE}/"]
    for language in languages.entries():
        urls.append(url(language["id"]))
        for bits in languages.key_sizes(language):
            for suffix, _ in TABS:
                urls.append(url(language["id"], bits, suffix))
    return urls


def render_links_txt() -> str:
    return "\n".join(all_urls()) + "\n"


def render_links_md() -> str:
    lines = [
        "# Link index",
        "",
        "Every address the showcase answers on. Generated from `langs/` by",
        "`python tools/generate_link_index.py` — do not edit by hand.",
        "",
        f"* Showcase: <{BASE}/>",
        f"* Repository: <{REPO}>",
        "* Protocol and tests: [README](../README.md#shared-console-protocol)",
        "",
        "The canonical address names the language and the key size, and the tab is",
        "appended only when it is not **Source Code**:",
        "",
        "```text",
        "/<language>/<bits>             Source Code (the default tab)",
        "/<language>/<bits>/overview    Overview",
        "/<language>/<bits>/output      Console Output",
        "```",
        "",
        "A bare `/<language>` opens that language at its first key size (`/c` → `/c/128`).",
        "GitHub Pages has no rewrite rules, so these routes are served through",
        "[`public/404.html`](../public/404.html), which rebuilds the address and hands it",
        "to the app — a `curl -I` can answer 404 even though the page loads.",
        "",
        f"The same list as plain text, one URL per line, is in [links.txt](links.txt) "
        f"({len(all_urls())} addresses).",
        "",
    ]

    for language in languages.entries():
        sizes = languages.key_sizes(language)
        lines += [
            f"## {language['name']} — {language['category']} (`{language['extension']}`)",
            "",
            "| Key size | Source Code | Overview | Console Output |",
            "| --- | --- | --- | --- |",
        ]
        for bits in sizes:
            cells = " | ".join(
                f"<{url(language['id'], bits, suffix)}>" for suffix, _ in TABS
            )
            lines.append(f"| {bits}-bit | {cells} |")
        lines += [
            "",
            f"Bare address: <{url(language['id'])}> (opens {sizes[0]}-bit).",
            f"Source: <{repo_url('langs/' + language['folder'])}>.",
            "",
        ]

    lines += [
        "## Older addresses",
        "",
        "Links shared before the key size moved into the address still work, and are",
        "canonicalised on load, so each pair opens the same page:",
        "",
        "| Older address | Canonical address |",
        "| --- | --- |",
        f"| <{BASE}/c-128> | <{url('c', 128)}> |",
        f"| <{BASE}/csharp-256> | <{url('csharp', 256)}> |",
        f"| <{BASE}/csharp-256/overview> | <{url('csharp', 256, '/overview')}> |",
        "",
        "## Repository links",
        "",
        "| What | Address |",
        "| --- | --- |",
        f"| Showcase root | <{BASE}/> |",
        f"| Repository | <{REPO}> |",
        f"| Protocol reference | <{REPO}/blob/{BRANCH}/tests/reference.py> |",
        f"| Test suite | <{REPO}/blob/{BRANCH}/tests/run_tests.py> |",
        f"| Expected output | <{REPO}/tree/{BRANCH}/tests/expected> |",
        f"| Language folders | <{REPO}/tree/{BRANCH}/langs> |",
        "",
    ]
    for language in languages.entries():
        lines.append(f"* {language['name']}: <{repo_url('langs/' + language['folder'])}>")
    lines.append("")

    return "\n".join(lines)


TARGETS = {
    DOCS / "links.md": render_links_md,
    DOCS / "links.txt": render_links_txt,
}


def main() -> int:
    check = "--check" in sys.argv[1:]
    stale: list[Path] = []

    DOCS.mkdir(parents=True, exist_ok=True)
    for path, render in TARGETS.items():
        text = render()
        if check:
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != text:
                stale.append(path)
        else:
            path.write_text(text, encoding="utf-8", newline="\n")
            print("wrote", path.relative_to(ROOT))

    if check:
        if stale:
            print("stale — run `python tools/generate_link_index.py`:")
            for path in stale:
                print(" -", path.relative_to(ROOT))
            return 1
        print("docs/links.md and docs/links.txt are up to date")

    return 0


if __name__ == "__main__":
    sys.exit(main())
