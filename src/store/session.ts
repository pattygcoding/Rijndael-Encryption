import { computed, reactive } from "vue";
import type { Implementation, LanguageEntry, TabId } from "../types";
import * as data from "./data";

export type MenuId = "category";

export interface FacetOption {
    value: string;
    label: string;
}

// ---- The address ----------------------------------------------------------------
// The sidebar names a language and the header dropdown names a key size, so an
// implementation is addressable as /c/128, /csharp/256/overview or
// /python-cryptography/256.  The dashboard is a static bundle, so the path is
// resolved client-side with the History API.  A document with a null origin
// (file://) refuses path writes, so the query shape (?lang=c&bits=256) is used
// there instead - and that query shape is also what the deployed site's 404.html
// shim forwards.  The older one-segment addresses (/c-128, /csharp-256/overview)
// are still understood, and canonicalised on load.
export const APP_DIR = window.location.pathname.replace(/[^/]*$/, "");
let applyingHistory = false;

// Can this document write a path?  Probing once here, rather than discovering it
// when the first write fails, keeps the sidebar's hrefs in the right shape from the
// very first render; the temporary URL is restored in the same tick.
const canWritePath = (function probePathWrites(): boolean {
    const original = window.location.href;
    try {
        window.history.replaceState(window.history.state, "", APP_DIR + "__path-probe__");
    } catch {
        return false;
    }
    try {
        window.history.replaceState(window.history.state, "", original);
    } catch {
        // keep going: the probe already told us path writes are allowed
    }
    return true;
})();

interface LocationState {
    langId: string | null;
    keySize: number | null;
    tab: TabId;
    explicitTab: boolean;
}

// A trailing tab segment names the tab; the one before it may name the key size.
const TAB_SEGMENT = /^(code|overview|output)$/;

// What the current address asks for, in either shape (and in the legacy one).
function locationState(): LocationState {
    const tail = window.location.pathname.slice(APP_DIR.length).replace(/\/+$/, "");
    const parts = tail ? tail.split("/") : [];
    const params = new URLSearchParams(window.location.search || "");

    let langId: string | null = null;
    let keySize: number | null = null;
    let tabSegment: TabId | null = null;
    let rest = parts;

    // The legacy single segment (`c-128`) carries both the language and the size.
    const legacy = parts[0] ? /^(.*)-(\d+)$/.exec(parts[0]) : null;
    if (legacy && data.knownLanguage(legacy[1])) {
        langId = legacy[1];
        keySize = Number(legacy[2]);
        rest = parts.slice(1);
    } else if (data.knownLanguage(parts[0])) {
        langId = parts[0];
        rest = parts.slice(1);
        if (rest.length && /^\d+$/.test(rest[0])) {
            keySize = Number(rest[0]);
            rest = rest.slice(1);
        }
    }

    if (rest.length && TAB_SEGMENT.test(rest[0])) {
        tabSegment = rest[0] as TabId;
    }

    // The query shape, used by file:// documents and by the 404 shim.
    if (!langId) {
        const fromQuery = params.get("lang");
        const legacyQuery = fromQuery ? /^(.*)-(\d+)$/.exec(fromQuery) : null;
        if (legacyQuery && data.knownLanguage(legacyQuery[1])) {
            langId = legacyQuery[1];
            keySize = Number(legacyQuery[2]);
        } else if (data.knownLanguage(fromQuery)) {
            langId = fromQuery;
        }
    }
    if (keySize === null) {
        const bits = params.get("bits");
        if (bits && /^\d+$/.test(bits)) {
            keySize = Number(bits);
        }
    }

    const rawTab = tabSegment ?? params.get("tab");
    return {
        langId,
        keySize,
        tab: rawTab === "overview" || rawTab === "output" ? rawTab : "code",
        explicitTab: !!(tabSegment || params.get("tab")),
    };
}

// The address for what is on screen, in whichever shape the browser accepts.  Used
// for the sidebar's real links too, so a copied or middle-clicked link carries the
// language, the key size and the tab.
export function stateUrl(langId: string, keySize: number, tab: TabId): string {
    // The query shape is only the fallback for documents that refuse path writes.
    if (!canWritePath) {
        const params = new URLSearchParams();
        params.set("lang", langId);
        params.set("bits", String(keySize));
        if (tab !== "code") {
            params.set("tab", tab);
        }
        return APP_DIR + "index.html?" + params.toString();
    }
    // Addresses stay clean: the source tab is the default, so it is not named.
    return APP_DIR + langId + "/" + keySize + (tab === "code" ? "" : "/" + tab);
}

function syncUrl(mode: "push" | "replace"): void {
    if (applyingHistory || !data.hasData || !state.langId) {
        return;
    }
    const url = stateUrl(state.langId, state.keySize, state.tab);
    try {
        if (mode === "push") {
            window.history.pushState(window.history.state, "", url);
        } else {
            window.history.replaceState(window.history.state, "", url);
        }
    } catch {
        // file:// refused the path write: the query shape was already used
    }
}

// ---- The reactive selection -----------------------------------------------------
// `langId` is the sidebar row (a language) and `keySize` is the header dropdown, so
// the two together name the implementation being shown.
export const state = reactive({
    langId: null as string | null,
    keySize: data.DEFAULT_KEY_SIZE,
    tab: "code" as TabId,
    query: "",
    category: "All",
    sidebarOpen: false,
    openMenu: null as MenuId | null,
});

export const currentItem = computed<Implementation | undefined>(() =>
    data.implementationFor(state.langId, state.keySize),
);

export const currentLanguage = computed(() => data.languageById(state.langId));

// The sizes the dropdown offers for the selected language - the standalone Python
// example only ships 256, so the list is per language rather than global.
export const availableKeySizes = computed<number[]>(() => data.keySizesFor(state.langId));

// The size to open a language at when moving between rows: the current size if that
// language ships it, otherwise the language's first.
export function keySizeFor(langId: string): number {
    const sizes = data.keySizesFor(langId);
    return sizes.includes(state.keySize) ? state.keySize : (sizes[0] ?? data.DEFAULT_KEY_SIZE);
}

// A key size taken from the address is honoured only when the language ships it.
function resolvedKeySize(langId: string | null, keySize: number | null): number {
    const sizes = data.keySizesFor(langId);
    return keySize !== null && sizes.includes(keySize) ? keySize : data.defaultKeySize(langId);
}

export const repoFolderName = computed<string>(() =>
    currentItem.value ? data.repoFolder(currentItem.value) : "",
);

export const repoUrl = computed<string>(() =>
    currentItem.value ? data.repoUrlFor(currentItem.value) : "",
);

// The verified capture from tests/expected, shown by the Console Output tab.
export const currentOutput = computed<string>(() => currentItem.value?.output ?? "");

export const outputAvailable = computed<boolean>(() => currentOutput.value.length > 0);

export const metaLine = computed<string>(() => {
    const meta = data.DATA?.meta;
    if (!meta) {
        return "";
    }
    return (
        (meta.entryCount ?? meta.languageCount) +
        " languages · " +
        meta.implementationCount +
        " implementations\nAES-128 · AES-192 · AES-256"
    );
});

export const searchPlaceholder = "Search languages…";

// The category facet counts sidebar rows, so its numbers match the list.
export const categoryOptions = computed<FacetOption[]>(() => {
    const rows = data.languages();
    const counts = new Map<string, number>();
    for (const row of rows) {
        counts.set(row.category, (counts.get(row.category) ?? 0) + 1);
    }
    const options: FacetOption[] = [
        { value: "All", label: "All categories (" + rows.length + ")" },
    ];
    for (const [name, count] of counts) {
        options.push({ value: name, label: name + " (" + count + ")" });
    }
    return options;
});

// One row per language; the key size is chosen in the header, not filtered here.
export const visibleLanguages = computed<LanguageEntry[]>(() => {
    const query = state.query.trim().toLowerCase();
    return data.languages().filter((language) => {
        if (state.category !== "All" && language.category !== state.category) {
            return false;
        }
        if (!query) {
            return true;
        }
        const haystack = (
            language.name + " " + language.category + " " + language.id
        ).toLowerCase();
        return haystack.includes(query);
    });
});

export const listMessage = computed<string>(() =>
    data.languages().length
        ? "No languages match those filters."
        : "No languages found.",
);

// ---- Moving around --------------------------------------------------------------
function applySelection(langId: string, keySize: number): void {
    state.langId = langId;
    state.keySize = keySize;
    syncUrl("push");
}

export function selectLanguage(id: string): void {
    // Keep the current key size when the new language ships it.
    applySelection(id, keySizeFor(id));
    // A tap on a list row ends that interaction, so the mobile drawer goes away.
    state.sidebarOpen = false;
}

// The header's key-size dropdown: the same language, a different file.
export function selectKeySize(keySize: number): void {
    if (state.keySize === keySize) {
        return;
    }
    state.keySize = keySize;
    syncUrl("push");
}

export function switchTab(tab: TabId): void {
    const changed = state.tab !== tab;
    state.tab = tab;
    if (changed) {
        syncUrl("push");
    }
}

export function setQuery(value: string): void {
    state.query = value;
}

export function setFacet(value: string): void {
    state.category = value;
}

export function toggleSidebar(): void {
    state.sidebarOpen = !state.sidebarOpen;
}

export function closeSidebar(): void {
    state.sidebarOpen = false;
}

export function toggleMenu(id: MenuId): void {
    state.openMenu = state.openMenu === id ? null : id;
}

export function closeMenus(): void {
    state.openMenu = null;
}

// Browser back/forward: mirror the address into the view, then canonicalise it.
function applyLocation(): void {
    if (!data.hasData) {
        return;
    }
    applyingHistory = true;
    const target = locationState();
    state.langId = target.langId ?? data.defaultLangId();
    state.keySize = resolvedKeySize(state.langId, target.keySize);
    state.tab = target.explicitTab ? target.tab : "code";
    applyingHistory = false;
    syncUrl("replace");
}

// Mirror the address into the view on load; the address is only written at the
// end, so a tab taken from the URL does not add a history entry.
export function initSession(): void {
    if (!data.hasData) {
        return;
    }
    const target = locationState();
    state.langId = target.langId ?? data.defaultLangId();
    state.keySize = resolvedKeySize(state.langId, target.keySize);
    state.tab = target.explicitTab ? target.tab : "code";
    syncUrl("replace");
    window.addEventListener("popstate", applyLocation);
}
