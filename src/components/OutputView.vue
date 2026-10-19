<script setup lang="ts">
import { ref } from "vue";
import { currentItem, currentOutput, outputAvailable } from "../store/session";

// The capture the suite verified: every language at this key size prints it.
const copied = ref(false);
let copyTimer: number | undefined;

async function copyOutput(): Promise<void> {
    if (!navigator.clipboard?.writeText) {
        return;
    }
    try {
        await navigator.clipboard.writeText(currentOutput.value);
    } catch {
        return;   // refused (insecure context or permissions): leave the icon alone
    }
    copied.value = true;
    window.clearTimeout(copyTimer);
    copyTimer = window.setTimeout(() => { copied.value = false; }, 1200);
}
</script>

<template>
    <section class="flex-1 flex flex-col min-h-0">
        <div class="flex items-center justify-between mb-2">
            <span class="micro text-fg-dim">Verified console output</span>
        </div>
        <p class="mb-3 text-xs leading-relaxed text-fg-muted">
            Every {{ currentItem?.name ?? "" }} implementation of a {{ currentItem?.keySize }}-bit key prints exactly
            this, line for line, and <code class="text-accent">python tests/run_tests.py</code> checks it against
            <code class="text-accent">tests/expected/aes-{{ currentItem?.keySize }}.txt</code>.
        </p>
        <div class="relative flex-1 min-h-0">
            <button v-if="outputAvailable" type="button" @click="copyOutput()" title="Copy console output"
                    aria-label="Copy console output"
                    :class="['absolute top-3 right-3 z-10 flex items-center justify-center w-8 h-8 rounded-md bg-ink-900/80 border border-line/10 backdrop-blur transition',
                             copied ? 'text-accent' : 'text-fg-muted hover:text-accent hover:border-accent/40']">
                <svg v-if="copied" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5" /></svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="14" height="14" x="8" y="8" rx="2" ry="2" /><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" /></svg>
            </button>
            <pre v-if="outputAvailable"
                 class="h-full overflow-auto rounded-lg bg-ink-850 border border-line/5 p-5 font-mono text-[13px] leading-relaxed text-fg-soft">{{ currentOutput }}</pre>
            <p v-else class="text-sm text-fg-muted">
                No verified output yet. Run <code class="text-accent">python tests/run_tests.py</code> and then
                <code class="text-accent">npm run data</code>.
            </p>
        </div>
    </section>
</template>
