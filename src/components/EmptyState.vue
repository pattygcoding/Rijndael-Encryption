<script setup lang="ts">
// Shown when public/encryption-data.js is missing (a fresh clone whose generator
// has not run yet): the app is still usable, and this says which command produces
// the data.
</script>

<template>
    <div class="flex-1 flex items-center justify-center text-center">
        <div>
            <p class="text-lg mb-2 text-fg-soft">No showcase data found.</p>
            <p class="text-sm text-fg-muted">Run <code class="text-accent">npm run data</code> to build
                <code class="text-accent">public/encryption-data.js</code>.</p>
        </div>
    </div>
</template>
