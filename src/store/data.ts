import type { DashboardData, Implementation, LanguageEntry } from "../types";

// Everything the dashboard displays, read straight from the generated payload.
// These helpers are pure lookups over `DATA` - the reactive selection on top of
// them lives in `session.ts`.
export const DATA: DashboardData | undefined = window.ENCRYPTION_DATA;

// A checkout that has not run the generator yet still boots and shows the empty
// state (which says how to generate the data) instead of throwing.
export const hasData: boolean =
    !!DATA && Array.isArray(DATA.languages) && DATA.languages.length > 0;

// The language the showcase opens when the address names none.  The C example is
// the reference walkthrough; a fork without it falls back to the first language
// present.  The key size comes from that language's own list.
export const DEFAULT_LANG_ID = "c";
export const DEFAULT_KEY_SIZE = 128;

// The last-resort repository, for a checkout that has not generated the data yet.
const DEFAULT_REPOSITORY = "https://github.com/pattygcoding/Rijndael-Encryption";

// The sidebar rows - one per language - and the flat implementation list behind
// them.
export function languages(): LanguageEntry[] {
    return DATA?.languages ?? [];
}

export function implementations(): Implementation[] {
    return DATA?.implementations ?? [];
}

export function languageById(id: string | null): LanguageEntry | undefined {
    if (!id) {
        return undefined;
    }
    return languages().find((language) => language.id === id);
}

export function knownLanguage(id: string | null | undefined): boolean {
    return !!id && languages().some((language) => language.id === id);
}

export function defaultLangId(): string | null {
    const all = languages();
    return (all.find((language) => language.id === DEFAULT_LANG_ID) ?? all[0])?.id ?? null;
}

// The key sizes a language ships, e.g. `[128, 192, 256]` - or just `[256]` for the
// standalone Python example, which is why the dropdown is built per language.
export function keySizesFor(langId: string | null): number[] {
    return languageById(langId)?.keySizes ?? [];
}

export function defaultKeySize(langId: string | null): number {
    return keySizesFor(langId)[0] ?? DEFAULT_KEY_SIZE;
}

// The implementation for a language at a key size.  A size the language does not
// ship falls back to its first, so a stale address still shows something real.
export function implementationFor(
    langId: string | null,
    keySize: number | null,
): Implementation | undefined {
    const language = languageById(langId);
    if (!language) {
        return undefined;
    }
    const size = keySize !== null && language.keySizes.includes(keySize)
        ? keySize
        : language.keySizes[0];
    return implementations().find(
        (item) => item.languageId === language.id && item.keySize === size,
    );
}

export function itemById(id: string | null): Implementation | undefined {
    if (!id) {
        return undefined;
    }
    return implementations().find((item) => item.id === id);
}

// The folder an implementation lives in, used for its GitHub link.
export function repoFolder(item: Implementation): string {
    return item.folder || item.file.replace(/\/[^/]*$/, "");
}

// `<repository>/tree/<branch>/<folder>`, with each path segment encoded so a
// folder such as `C#` becomes `C%23` instead of a fragment.
export function repoUrlFor(item: Implementation): string {
    const repository = DATA?.meta?.repository;
    if (!repository) {
        return "";
    }
    const folder = repoFolder(item)
        .split("/")
        .map((segment) => encodeURIComponent(segment))
        .join("/");
    return repository + "/tree/" + (DATA?.meta?.branch || "main") + "/" + folder;
}

// The repository root itself, behind the sidebar's GitHub mark.
export function repoHomeUrl(): string {
    return DATA?.meta?.repository || DEFAULT_REPOSITORY;
}

// A language's short file-extension tag (".ts", ".cs"), used by the list badges.
export function languageTag(name: string): string {
    return DATA?.languageExtensions?.[name] ?? name;
}

// The line-number column beside the code: one number per line, trimmed of the
// trailing blank lines a file ends with.
export function lineNumbersFor(text: string): string {
    const normalized = text.replace(/\n+$/, "");
    const count = normalized.length ? normalized.split("\n").length : 1;
    const numbers: number[] = [];
    for (let line = 1; line <= count; line += 1) {
        numbers.push(line);
    }
    return numbers.join("\n");
}
