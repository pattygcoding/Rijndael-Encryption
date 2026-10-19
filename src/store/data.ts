import type { DashboardData, Implementation } from "../types";

// Everything the dashboard displays, read straight from the generated payload.
// These helpers are pure lookups over `DATA` - the reactive selection on top of
// them lives in `session.ts`.
export const DATA: DashboardData | undefined = window.ENCRYPTION_DATA;

// A checkout that has not run the generator yet still boots and shows the empty
// state (which says how to generate the data) instead of throwing.
export const hasData: boolean =
    !!DATA && Array.isArray(DATA.implementations) && DATA.implementations.length > 0;

// The implementation the showcase opens when the address names none.  The C
// 128-bit example is the reference walkthrough; a fork without it falls back to
// the first implementation present.
export const DEFAULT_IMPL_ID = "c-128";

// The last-resort repository, for a checkout that has not generated the data yet.
const DEFAULT_REPOSITORY = "https://github.com/pattygcoding/Rijndael-Encryption";

export function implementations(): Implementation[] {
    return DATA?.implementations ?? [];
}

export function itemById(id: string | null): Implementation | undefined {
    if (!id) {
        return undefined;
    }
    return implementations().find((item) => item.id === id);
}

export function knownLang(id: string | null | undefined): boolean {
    return !!id && implementations().some((item) => item.id === id);
}

export function defaultLangId(): string | null {
    const all = implementations();
    return (all.find((item) => item.id === DEFAULT_IMPL_ID) ?? all[0])?.id ?? null;
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
