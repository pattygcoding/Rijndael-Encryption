// The shape of `public/encryption-data.js`, which tools/generate-data.mjs writes
// from the real repository.  Every renderer works from this one shape.

export type TabId = "code" | "overview" | "output";

export interface Implementation {
    /** The implementation address slug, e.g. `c-128`. */
    id: string;
    /** The language row in the sidebar this implementation belongs to, e.g. `c`. */
    languageId: string;
    /** The language name shown in the list, e.g. `C#`. */
    name: string;
    /** The language family, e.g. `Python` for the standalone example. */
    language: string;
    category: string;
    keySize: number;
    /** The Prism grammar class, e.g. `language-csharp`. */
    prism: string;
    /** The crypto library the implementation calls. */
    api: string;
    /** The block cipher mode read from the source (CBC, CTR, ...). */
    mode: string;
    /** The source path shown above the code and linked on GitHub. */
    file: string;
    /** The folder the GitHub link points at. */
    folder: string;
    /** The verified output every implementation of this key size prints. */
    output: string;
    code: string;
}

/** One sidebar row: a language and the key sizes it ships. */
export interface LanguageEntry {
    id: string;
    name: string;
    category: string;
    prism: string;
    /** The file-extension tag shown in the list, e.g. `.cs`. */
    extension: string;
    /** The key sizes this language implements, e.g. `[128, 192, 256]`. */
    keySizes: number[];
}

export interface DataMeta {
    updated: string;
    implementationCount: number;
    languageCount: number;
    /** Sidebar rows (languages plus the standalone Python variant). */
    entryCount: number;
    repository: string;
    branch: string;
}

export interface DashboardData {
    meta: DataMeta;
    keySizes: number[];
    languages: LanguageEntry[];
    implementations: Implementation[];
    /** language name -> its file-extension tag (".ts", ".cs", ...). */
    languageExtensions: Record<string, string>;
}

declare global {
    interface Window {
        /** Installed by public/encryption-data.js, before the app module runs. */
        ENCRYPTION_DATA?: DashboardData;
    }
}
