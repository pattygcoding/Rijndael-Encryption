<script setup lang="ts">
import { keySizeFor, listMessage, selectLanguage, state, stateUrl, visibleLanguages } from "../store/session";

// The list is real links, so every language can be copied, bookmarked or opened in
// a new tab; a plain left click stays in the page.  A row carries the key size that
// is currently selected (when the language ships it), so switching language keeps
// the size you were reading.
function onSelect(event: MouseEvent, id: string): void {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
        return;
    }
    event.preventDefault();
    selectLanguage(id);
}
</script>

<template>
    <nav class="overflow-y-auto flex-1 p-2 space-y-1">
        <p v-if="visibleLanguages.length === 0" class="micro text-fg-dim px-3 py-2">{{ listMessage }}</p>
        <a v-else v-for="language in visibleLanguages" :key="language.id"
           :href="stateUrl(language.id, keySizeFor(language.id), state.tab)"
           :aria-current="language.id === state.langId ? 'page' : undefined"
           :class="['w-full text-left px-3 py-2.5 rounded-md text-sm font-medium transition flex items-center justify-between gap-2',
                    language.id === state.langId
                        ? 'bg-accent/10 text-accent border border-accent/30'
                        : 'text-fg-soft hover:bg-line/5 border border-transparent']"
           @click="onSelect($event, language.id)">
            <span class="truncate">{{ language.name }}</span>
            <!-- Badges: the category, the key size when the language ships only one,
                 and the blue file-extension tag. -->
            <span class="flex items-center gap-1 shrink-0">
                <span class="micro px-1.5 py-0.5 rounded border border-line/10 text-fg-dim">{{ language.category }}</span>
                <span v-if="language.keySizes.length === 1"
                      class="micro px-1.5 py-0.5 rounded border border-accent/30 text-accent/90"
                      :title="language.keySizes[0] + '-bit only'">{{ language.keySizes[0] }}</span>
                <span class="lang-tag" :title="language.name">{{ language.extension }}</span>
            </span>
        </a>
    </nav>
</template>
