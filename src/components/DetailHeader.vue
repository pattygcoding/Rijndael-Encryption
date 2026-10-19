<script setup lang="ts">
import { computed } from "vue";
import type { TabId } from "../types";
import { languageTag } from "../store/data";
import {
    currentItem,
    repoFolderName,
    repoUrl,
    state,
    switchTab,
    toggleSidebar,
} from "../store/session";
import { toggleTheme } from "../store/theme";

const title = computed<string>(() =>
    currentItem.value ? currentItem.value.name + " Implementation" : "Select an implementation",
);

// The repo link reads as a label rather than a URL, and names the folder it points
// at inside the project the data came from.
const repoLabel = computed<string>(() =>
    repoFolderName.value ? "View " + repoFolderName.value + " on GitHub" : "",
);

// The active tab keeps its filled look; the other stays muted.
function tabClass(tab: TabId): string {
    return "px-4 py-1.5 rounded text-sm font-medium transition " +
        (state.tab === tab ? "bg-mint-400 text-on-accent" : "text-fg-muted hover:text-fg");
}
</script>

<template>
    <header class="bg-ink-900/80 backdrop-blur border-b border-line/5 px-4 sm:px-5 py-4 flex flex-wrap gap-3 justify-between items-center">
        <div class="flex items-start gap-3 min-w-0">
            <button type="button" @click="toggleSidebar()"
                    aria-label="Toggle navigation" :aria-expanded="state.sidebarOpen" aria-controls="sidebar"
                    class="lg:hidden shrink-0 mt-0.5 flex items-center justify-center w-9 h-9 rounded-md bg-ink-950 border border-line/10 text-fg-muted hover:text-accent hover:border-accent/40 transition">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 6h16" /><path d="M4 12h16" /><path d="M4 18h16" /></svg>
            </button>
            <div class="min-w-0">
                <p class="micro text-fg-dim">Selected implementation</p>
                <h2 class="mt-1.5 text-lg font-semibold tracking-tight truncate text-fg-strong">{{ title }}</h2>
                <p class="mt-0.5 text-xs text-fg-muted font-mono truncate">{{ currentItem?.file ?? "" }}</p>
                <a v-if="repoUrl" :href="repoUrl" :title="repoUrl" target="_blank" rel="noopener"
                   class="mt-1.5 inline-flex items-center gap-1.5 max-w-full text-[11px] font-mono text-fg-dim hover:text-accent transition">
                    <span class="shrink-0 flex" aria-hidden="true">
                        <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" /><path d="M9 18c-4.51 2-5-2-7-2" /></svg>
                    </span>
                    <span class="truncate min-w-0">{{ repoLabel }}</span>
                </a>
                <div v-if="currentItem" class="mt-2 flex flex-wrap items-center gap-1.5">
                    <span class="lang-tag" :title="currentItem.language">{{ languageTag(currentItem.language) }}</span>
                    <span class="micro px-1.5 py-0.5 rounded border border-accent/30 text-accent/90">{{ currentItem.keySize }}-bit key</span>
                    <span class="micro px-1.5 py-0.5 rounded border border-line/10 text-fg-dim">{{ currentItem.category }}</span>
                </div>
            </div>
        </div>
        <div class="flex flex-wrap items-center gap-3">
            <div class="flex space-x-1 bg-ink-900 border border-line/5 p-1 rounded-md">
                <button type="button" @click="switchTab('code')" :class="tabClass('code')">Source Code</button>
                <button type="button" @click="switchTab('overview')" :class="tabClass('overview')">Overview</button>
            </div>
            <button type="button" @click="toggleTheme()" title="Switch colour theme" aria-label="Switch colour theme"
                    class="flex items-center justify-center w-9 h-9 rounded-md bg-ink-950 border border-line/10 text-fg-muted hover:text-accent hover:border-accent/40 transition">
                <span class="theme-icon-sun flex" aria-hidden="true">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4" /><path d="M12 2v2" /><path d="M12 20v2" /><path d="m4.93 4.93 1.41 1.41" /><path d="m17.66 17.66 1.41 1.41" /><path d="M2 12h2" /><path d="M20 12h2" /><path d="m6.34 17.66-1.41 1.41" /><path d="m19.07 4.93-1.41 1.41" /></svg>
                </span>
                <span class="theme-icon-moon flex" aria-hidden="true">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" /></svg>
                </span>
            </button>
        </div>
    </header>
</template>
