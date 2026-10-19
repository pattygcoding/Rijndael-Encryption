"""The canonical language registry shared by the tooling in this folder.

`id` is the address slug the dashboard uses (`/c/256`), `folder` is the directory
under `langs/`, and `extension` is the file-extension tag shown in the sidebar.
Keeping it in one importable module means the README generator, the link index and
the test suite can be checked against the same list.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LANGUAGES: list[dict] = [
    {"id": "c", "name": "C", "folder": "C", "extension": ".c", "category": "Systems"},
    {"id": "csharp", "name": "C#", "folder": "C#", "extension": ".cs", "category": ".NET"},
    {"id": "cpp", "name": "C++", "folder": "C++", "extension": ".cpp", "category": "Systems"},
    {"id": "haskell", "name": "Haskell", "folder": "Haskell", "extension": ".hs", "category": "Functional"},
    {"id": "java", "name": "Java", "folder": "Java", "extension": ".java", "category": "JVM"},
    {"id": "javascript", "name": "JavaScript", "folder": "JavaScript", "extension": ".js", "category": "Web"},
    {"id": "kotlin", "name": "Kotlin", "folder": "Kotlin", "extension": ".kt", "category": "JVM"},
    {"id": "php", "name": "PHP", "folder": "PHP", "extension": ".php", "category": "Scripting"},
    {"id": "python", "name": "Python", "folder": "Python", "extension": ".py", "category": "Scripting"},
    {"id": "ruby", "name": "Ruby", "folder": "Ruby", "extension": ".rb", "category": "Scripting"},
    {"id": "typescript", "name": "TypeScript", "folder": "TypeScript", "extension": ".ts", "category": "Web"},
]

# The one implementation that is not organised by key size: it lives in the Python
# folder but is its own sidebar row and its own address.
EXTRAS: list[dict] = [
    {
        "id": "python-cryptography",
        "name": "Python (cryptography)",
        "folder": "Python",
        "extension": ".py",
        "category": "Scripting",
        "keySizes": [256],
    },
]


def key_sizes(language: dict) -> list[int]:
    """The key sizes a language ships - read from `langs/<folder>/<bits>bit/`."""
    if "keySizes" in language:
        return list(language["keySizes"])
    folder = ROOT / "langs" / language["folder"]
    sizes = [
        int(path.name[: -len("bit")])
        for path in folder.glob("*bit")
        if path.is_dir() and path.name[: -len("bit")].isdigit()
    ]
    return sorted(sizes)


def entries() -> list[dict]:
    """Every sidebar row, in the order the dashboard lists them."""
    return LANGUAGES + EXTRAS
