import { computed, reactive } from "vue";
import type { Implementation, TabId } from "../types";
import * as data from "./data";

export type MenuId = "category" | "keySize";

export interface FacetOption {
    value: string;
    label: string;
}

// ---- The address ----------------------------------------------------------------
// Every implementation is addressable on its own path: /c-128, /csharp-256,
// /python-cryptography.  The dashboard is a static bundle, so the path is resolved
// client-side with the History API.  A document with a null origin (file://) refuses
// path writes, so the query-string shape (?lang=c-128) is used there instead - and
// that query shape is also what the deployed site's 404.html shim forwards, so
// `?lang=` and `?tab=` stay readable in both forms and older links keep working.
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
    tab: TabId;
    explicit: boolean;
}

// What the current address asks for, in either shape.
function locationState(): LocationState {
    const tail = window.location.pathname.slice(APP_DIR.length).replace(/\/+$/, "");
    const parts = tail ? tail.split("/") : [];
    const pathTab = parts.length === 2 && /^(code|overview|output)$/.test(parts[1])
        ? (parts[1] as TabId)
        : null;
    const params = new URLSearchParams(window.location.search || "");
    const langId = data.knownLang(parts[0]) ? parts[0] : params.get("lang");
    const rawTab = pathTab || params.get("tab");
    return {
        langId: data.knownLang(langId) ? langId : null,
        tab: rawTab === "overview" || rawTab === "output" ? rawTab : "code",
        explicit: !!(pathTab || params.get("tab")),
    };
}

// The address for what is on screen, in whichever shape the browser accepts.  Used
// for the sidebar's real links too, so a copied or middle-clicked link carries the
// current tab along with the implementation.
export function stateUrl(langId: string, tab: TabId): string {
    // The query shape is only the fallback for documents that refuse path writes.
    // Addresses otherwise stay clean: the source tab is the default, so it is not
    // named, and the Overview tab is a path segment (`/csharp-256/overview`).
    if (!canWritePath) {
        const params = new URLSearchParams();
        params.set("lang", langId);
        if (tab !== "code") {
            params.set("tab", tab);
        }
        return APP_DIR + "index.html?" + params.toString();
    }
    return APP_DIR + langId + (tab === "code" ? "" : "/" + tab);
}

function syncUrl(mode: "push" | "replace"): void {
    if (applyingHistory || !data.hasData || !state.langId) {
        return;
    }
    const url = stateUrl(state.langId, state.tab);
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
export const state = reactive({
    langId: null as string | null,
    tab: "code" as TabId,
    query: "",
    category: "All",
    keySize: "All",
    sidebarOpen: false,
    openMenu: null as MenuId | null,
});

export const currentItem = computed<Implementation | undefined>(() =>
    data.itemById(state.langId),
);

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
        meta.languageCount +
        " languages · " +
        meta.implementationCount +
        " implementations\nAES-128 · AES-192 · AES-256"
    );
});

export const searchPlaceholder = "Search languages or files…";

// The facet menus.  Counts make the list self-explanatory and keep every option
// visibly tied to the filtered set.
export const categoryOptions = computed<FacetOption[]>(() => {
    const items = data.implementations();
    const counts = new Map<string, number>();
    for (const item of items) {
        counts.set(item.category, (counts.get(item.category) ?? 0) + 1);
    }
    const options: FacetOption[] = [
        { value: "All", label: "All categories (" + items.length + ")" },
    ];
    for (const [name, count] of counts) {
        options.push({ value: name, label: name + " (" + count + ")" });
    }
    return options;
});

export const keySizeOptions = computed<FacetOption[]>(() => {
    const items = data.implementations();
    const options: FacetOption[] = [{ value: "All", label: "All key sizes" }];
    for (const size of data.DATA?.keySizes ?? []) {
        const count = items.filter((item) => item.keySize === size).length;
        options.push({ value: String(size), label: size + "-bit (" + count + ")" });
    }
    return options;
});

export const visibleItems = computed<Implementation[]>(() => {
    const query = state.query.trim().toLowerCase();
    return data.implementations().filter((item) => {
        if (state.category !== "All" && item.category !== state.category) {
            return false;
        }
        if (state.keySize !== "All" && String(item.keySize) !== state.keySize) {
            return false;
        }
        if (!query) {
            return true;
        }
        const haystack = (
            item.name +
            " " +
            item.file +
            " " +
            item.category +
            " " +
            item.keySize
        ).toLowerCase();
        return haystack.includes(query);
    });
});

export const listMessage = computed<string>(() =>
    data.implementations().length
        ? "No implementations match those filters."
        : "No implementations found.",
);

// ---- Moving around --------------------------------------------------------------
function applySelection(id: string): void {
    state.langId = id;
    syncUrl("push");
}

export function selectLanguage(id: string): void {
    applySelection(id);
    // A tap on a list row ends that interaction, so the mobile drawer goes away.
    state.sidebarOpen = false;
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

export function setFacet(id: "category" | "keySize", value: string): void {
    state[id] = value;
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
    state.tab = target.explicit ? target.tab : "code";
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
    state.tab = target.explicit ? target.tab : "code";
    syncUrl("replace");
    window.addEventListener("popstate", applyLocation);
}
