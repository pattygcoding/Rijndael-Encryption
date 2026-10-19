<script setup lang="ts">
import { computed } from "vue";
import { currentItem, repoUrl } from "../store/session";

// The facts the generator recorded for this implementation, laid out as cards.
const facts = computed(() => {
    const item = currentItem.value;
    if (!item) {
        return [];
    }
    return [
        { label: "Language", value: item.name },
        { label: "Key size", value: item.keySize + "-bit" },
        { label: "Block size", value: "128-bit" },
        { label: "Mode", value: item.mode },
        { label: "Library", value: item.api },
        { label: "Category", value: item.category },
        { label: "Source", value: item.file },
    ];
});
</script>

<template>
    <section class="flex-1 min-h-0 overflow-auto">
        <div class="max-w-4xl pb-6">
            <p class="micro text-fg-dim">Implementation overview</p>
            <h3 v-if="currentItem" class="mt-2 text-2xl font-semibold tracking-tight text-fg-strong">
                AES-{{ currentItem.keySize }} in {{ currentItem.name }}
            </h3>
            <p v-if="currentItem" class="mt-3 max-w-2xl text-sm leading-relaxed text-fg-muted">
                This example encrypts a test message with a {{ currentItem.keySize }}-bit key using
                <span class="text-fg-soft">{{ currentItem.api }}</span> in
                <span class="text-fg-soft">{{ currentItem.mode }}</span> mode. The full, runnable source is
                on the <span class="text-fg-soft">Source Code</span> tab.
            </p>

            <div class="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                <div v-for="fact in facts" :key="fact.label"
                     class="rounded-lg bg-ink-850 border border-line/5 px-4 py-3">
                    <p class="micro text-fg-dim">{{ fact.label }}</p>
                    <p class="mt-1 text-sm font-mono break-words text-fg-soft">{{ fact.value }}</p>
                </div>
            </div>

            <div class="mt-6 rounded-lg bg-ink-850 border border-line/5 p-5">
                <p class="micro text-fg-dim">About Rijndael / AES</p>
                <p class="mt-2 text-sm leading-relaxed text-fg-muted">
                    Rijndael is the block cipher selected as the Advanced Encryption Standard. AES is its
                    standardized subset: a fixed 128-bit block with a 128-, 192- or 256-bit key, applied
                    here in one of the classic modes (CBC or CTR) with a fresh key per run.
                </p>
                <p class="mt-3 text-sm leading-relaxed text-fg-muted">
                    Because every implementation generates a random key — and a random IV wherever the
                    mode uses one — the ciphertext it prints changes on each run. That is why this
                    showcase compares the source of each implementation rather than captured output.
                </p>
            </div>

            <a v-if="repoUrl" :href="repoUrl" target="_blank" rel="noopener"
               class="mt-4 inline-flex items-center gap-1.5 text-sm text-accent hover:underline">
                Open {{ currentItem?.folder }} on GitHub
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7" /><path d="M7 7h10v10" /></svg>
            </a>
        </div>
    </section>
</template>
