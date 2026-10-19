#!/usr/bin/env python3
"""Run every implementation and compare its output with the shared expected text.

Each implementation prints the five lines described in ``tests/reference.py`` for
its key size, so the same deterministic ciphertext must come out of every language:

    python tests/run_tests.py                # run everything
    python tests/run_tests.py --filter java  # only matching cases
    python tests/run_tests.py --update       # regenerate tests/expected from reference.py

The expected files are committed, so the suite is a real regression test: changing
an implementation so it no longer matches fails the run.  A toolchain that is not
installed on the machine is reported as SKIP rather than FAIL.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"
BUILD = TESTS / "build"
EXPECTED = TESTS / "expected"

sys.path.insert(0, str(TESTS))
import reference  # noqa: E402


@dataclass
class Case:
    id: str
    label: str
    source: str
    bits: int
    kind: str


LANGUAGES = [
    ("c", "C", "langs/C/{bits}bit/Rijndael.c", "c"),
    ("cpp", "C++", "langs/C++/{bits}bit/Rijndael.cpp", "cpp"),
    ("csharp", "C#", "langs/C#/{bits}bit/Rijndael.cs", "csharp"),
    ("haskell", "Haskell", "langs/Haskell/{bits}bit/Rijndael.hs", "haskell"),
    ("java", "Java", "langs/Java/{bits}bit/Rijndael.java", "java"),
    ("javascript", "JavaScript", "langs/JavaScript/{bits}bit/Rijndael.js", "node"),
    ("kotlin", "Kotlin", "langs/Kotlin/{bits}bit/Rijndael.kt", "kotlin"),
    ("php", "PHP", "langs/PHP/{bits}bit/Rijndael.php", "php"),
    ("python", "Python", "langs/Python/{bits}bit/Rijndael.py", "python"),
    ("ruby", "Ruby", "langs/Ruby/{bits}bit/Rijndael.rb", "ruby"),
    ("typescript", "TypeScript", "langs/TypeScript/{bits}bit/Rijndael.ts", "typescript"),
]

EXTRA_CASES = [
    ("python-cryptography", "Python (cryptography)", "langs/Python/rijndael.py", 256, "python"),
]


def build_cases() -> list[Case]:
    cases: list[Case] = []
    for size in reference.KEY_SIZES:
        for slug, label, template, kind in LANGUAGES:
            cases.append(
                Case(
                    id=f"{slug}-{size}",
                    label=f"{label} ({size}-bit)",
                    source=template.format(bits=size),
                    bits=size,
                    kind=kind,
                )
            )
    for slug, label, source, bits, kind in EXTRA_CASES:
        cases.append(Case(id=slug, label=label, source=source, bits=bits, kind=kind))
    return cases


def normalize(text: str) -> str:
    """Line endings and trailing blank lines differ per platform; nothing else may."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    while lines and lines[-1].strip() == "":
        lines.pop()
    return "\n".join(lines)


def run(command: list[str], env: dict[str, str] | None = None, timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run(
        _runnable(command),
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def _runnable(command: list[str]) -> list[str]:
    """Resolve the program, routing Windows `.cmd`/`.bat` shims through cmd.exe."""
    executable = shutil.which(command[0]) or command[0]
    if executable.lower().endswith((".bat", ".cmd")):
        return [os.environ.get("COMSPEC", "cmd.exe"), "/c", executable, *command[1:]]
    return [executable, *command[1:]]


# --------------------------------------------------------------------------- OpenSSL
_OPENSSL: dict | None = None


def _pkg_config(*args: str) -> str:
    # On Windows pkg-config is often a `.cmd` shim, which CreateProcess cannot run
    # directly, so anything script-shaped goes through the command interpreter.
    executable = shutil.which("pkg-config")
    if executable is None:
        return ""
    command = [executable, *args]
    if executable.lower().endswith((".bat", ".cmd")):
        command = [os.environ.get("COMSPEC", "cmd.exe"), "/c", *command]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def openssl() -> dict:
    """Include/lib/bin directories and link flags for OpenSSL, wherever it lives."""
    global _OPENSSL
    if _OPENSSL is not None:
        return _OPENSSL

    candidates: list[Path] = []
    configured = os.environ.get("OPENSSL_DIR")
    if configured:
        candidates.append(Path(configured))
    prefix = _pkg_config("--variable=prefix", "openssl")
    if prefix:
        candidates.append(Path(prefix))
    candidates += [
        Path("C:/Program Files/OpenSSL-Win64"),
        Path("C:/Program Files/OpenSSL"),
        Path("/usr"),
        Path("/usr/local"),
        Path("/opt/homebrew/opt/openssl"),
    ]

    windows_extras = ["-lws2_32", "-lcrypt32"] if sys.platform == "win32" else []
    for root in candidates:
        include = root / "include"
        if not (include / "openssl" / "evp.h").exists():
            continue
        library = root / "lib"
        libs = _pkg_config("--libs", "openssl").split() or ["-lssl", "-lcrypto"]
        binary = root / "bin"
        _OPENSSL = {
            "cflags": [f"-I{include}"],
            "libs": [f"-L{library}"] + libs + windows_extras,
            "path": str(binary) if binary.exists() else None,
        }
        return _OPENSSL

    _OPENSSL = {
        "cflags": _pkg_config("--cflags", "openssl").split(),
        "libs": _pkg_config("--libs", "openssl").split() or ["-lssl", "-lcrypto"],
        "path": None,
    }
    return _OPENSSL


# --------------------------------------------------------------------------- Builders
CSHARP_PROJECT = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>disable</ImplicitUsings>
    <Nullable>disable</Nullable>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
    <AssemblyName>{name}</AssemblyName>
  </PropertyGroup>
  <ItemGroup>
    <Compile Include="{source}" />
  </ItemGroup>
</Project>
"""


def plan(case: Case) -> tuple[list[list[str]], list[str], dict[str, str], str | None]:
    """Return the build steps, the run command, the environment and any missing tool."""
    source = ROOT / case.source
    workdir = BUILD / case.id
    workdir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    suffix = ".exe" if sys.platform == "win32" else ""

    if case.kind in ("c", "cpp"):
        compiler_name = "gcc" if case.kind == "c" else "g++"
        compiler = shutil.which(compiler_name)
        if compiler is None:
            return [], [], env, compiler_name
        flags = openssl()
        executable = workdir / f"{case.id}{suffix}"
        steps = [[
            compiler,
            str(source),
            "-O2",
            "-o",
            str(executable),
            *flags["cflags"],
            *flags["libs"],
        ]]
        if flags["path"]:
            env["PATH"] = flags["path"] + os.pathsep + env.get("PATH", "")
        return steps, [str(executable)], env, None

    if case.kind == "csharp":
        if shutil.which("dotnet") is None:
            return [], [], env, "dotnet"
        project = workdir / f"{case.id}.csproj"
        project.write_text(
            CSHARP_PROJECT.format(name=case.id, source=source),
            encoding="utf-8",
        )
        output = workdir / "out"
        steps = [["dotnet", "build", str(project), "-c", "Release", "-o", str(output), "--nologo", "-v", "q"]]
        return steps, ["dotnet", str(output / f"{case.id}.dll")], env, None

    if case.kind == "haskell":
        if shutil.which("ghc") is None:
            return [], [], env, "ghc"
        executable = workdir / f"{case.id}{suffix}"
        steps = [[
            "ghc",
            "-package", "cryptonite",
            "-package", "memory",
            "-package", "bytestring",
            "-package", "base",
            str(source),
            "-o", str(executable),
            "-outputdir", str(workdir / "obj"),
        ]]
        return steps, [str(executable)], env, None

    if case.kind == "java":
        if shutil.which("javac") is None:
            return [], [], env, "javac"
        classes = workdir / "classes"
        steps = [["javac", "-d", str(classes), str(source)]]
        return steps, ["java", "-cp", str(classes), "Rijndael"], env, None

    if case.kind == "kotlin":
        if shutil.which("kotlinc") is None:
            return [], [], env, "kotlinc"
        jar = workdir / f"{case.id}.jar"
        steps = [["kotlinc", str(source), "-include-runtime", "-d", str(jar)]]
        return steps, ["java", "-jar", str(jar)], env, None

    if case.kind == "typescript":
        tsc = ROOT / "node_modules" / ".bin" / ("tsc.cmd" if sys.platform == "win32" else "tsc")
        if not tsc.exists():
            return [], [], env, "typescript (run npm install)"
        output = workdir / "js"
        steps = [[
            str(tsc),
            str(source),
            "--outDir", str(output),
            "--module", "nodenext",
            "--moduleResolution", "nodenext",
            "--target", "ES2022",
            "--types", "node",
            "--skipLibCheck",
        ]]
        return steps, ["node", str(output / "Rijndael.js")], env, None

    if case.kind == "node":
        if shutil.which("node") is None:
            return [], [], env, "node"
        return [], ["node", str(source)], env, None

    if case.kind == "php":
        if shutil.which("php") is None:
            return [], [], env, "php"
        return [], ["php", "-d", "extension=openssl", str(source)], env, None

    if case.kind == "python":
        return [], [sys.executable, str(source)], env, None

    if case.kind == "ruby":
        if shutil.which("ruby") is None:
            return [], [], env, "ruby"
        return [], ["ruby", str(source)], env, None

    raise ValueError(f"unknown implementation kind: {case.kind}")


# --------------------------------------------------------------------------- Runner
def expected_text(bits: int) -> str:
    return (EXPECTED / f"aes-{bits}.txt").read_text(encoding="utf-8")


def update_expected() -> None:
    EXPECTED.mkdir(parents=True, exist_ok=True)
    for size in reference.KEY_SIZES:
        path = EXPECTED / f"aes-{size}.txt"
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(reference.output(size))
        print(f"wrote {path.relative_to(ROOT)}")


def first_difference(expected: str, actual: str) -> str:
    expected_lines = expected.split("\n")
    actual_lines = actual.split("\n")
    for index in range(max(len(expected_lines), len(actual_lines))):
        want = expected_lines[index] if index < len(expected_lines) else "<missing>"
        got = actual_lines[index] if index < len(actual_lines) else "<missing>"
        if want != got:
            return f"  line {index + 1}\n    expected: {want}\n    actual:   {got}"
    return "  (no line-level difference)"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run every implementation against the shared expected output.")
    parser.add_argument("--filter", help="only run cases whose id or label contains this text")
    parser.add_argument("--update", action="store_true", help="regenerate tests/expected from tests/reference.py")
    parser.add_argument("--list", action="store_true", help="list the cases without running them")
    args = parser.parse_args()

    if args.update:
        update_expected()
        return 0

    cases = build_cases()
    if args.filter:
        needle = args.filter.lower()
        cases = [case for case in cases if needle in case.id.lower() or needle in case.label.lower()]
    if args.list:
        for case in cases:
            print(f"{case.id:<24} {case.label:<24} {case.source}")
        return 0

    if not cases:
        print("no cases matched")
        return 1

    BUILD.mkdir(parents=True, exist_ok=True)

    passed: list[str] = []
    skipped: list[tuple[str, str]] = []
    failed: list[tuple[Case, str]] = []

    for case in cases:
        steps, command, env, missing = plan(case)
        if missing:
            print(f"SKIP  {case.label}: {missing} not found")
            skipped.append((case.label, missing))
            continue

        build_failure = ""
        for step in steps:
            try:
                result = run(step, env)
            except subprocess.TimeoutExpired:
                build_failure = f"timed out: {' '.join(step)}"
                break
            if result.returncode != 0:
                build_failure = (result.stdout + result.stderr).strip()[-2000:]
                break
        if build_failure:
            print(f"FAIL  {case.label}: build failed")
            failed.append((case, f"build failed\n{build_failure}"))
            continue

        try:
            result = run(command, env)
        except subprocess.TimeoutExpired:
            print(f"FAIL  {case.label}: timed out")
            failed.append((case, "timed out"))
            continue

        if result.returncode != 0:
            print(f"FAIL  {case.label}: exited with {result.returncode}")
            failed.append((case, f"exit {result.returncode}\n{(result.stdout + result.stderr).strip()[-1000:]}"))
            continue

        expected = normalize(expected_text(case.bits))
        actual = normalize(result.stdout)
        if actual == expected:
            print(f"PASS  {case.label}")
            passed.append(case.label)
        else:
            print(f"FAIL  {case.label}: output does not match tests/expected/aes-{case.bits}.txt")
            failed.append((case, "output mismatch\n" + first_difference(expected, actual)))

    print()
    print(f"{len(passed)} passed, {len(failed)} failed, {len(skipped)} skipped")

    if failed:
        print()
        for case, detail in failed:
            print(f"--- {case.label} ({case.source})")
            print(detail)
    if skipped:
        print()
        print("Skipped toolchains: " + ", ".join(f"{label} ({tool})" for label, tool in skipped))

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
