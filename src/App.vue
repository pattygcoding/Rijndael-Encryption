<script setup lang="ts">
import { onBeforeUnmount, onMounted } from "vue";
import AppSidebar from "./components/AppSidebar.vue";
import DetailHeader from "./components/DetailHeader.vue";
import EmptyState from "./components/EmptyState.vue";
import OutputView from "./components/OutputView.vue";
import OverviewView from "./components/OverviewView.vue";
import SourceView from "./components/SourceView.vue";
import { hasData } from "./store/data";
import { closeMenus, closeSidebar, state } from "./store/session";

// Menus are custom dropdowns (an OS-drawn <select> popup cannot be height-capped),
// so an outside click or Escape closes them; Escape also puts the mobile drawer
// away.  The listeners live here so they are torn down with the app.
function onDocumentClick(): void {
    closeMenus();
}

function onKeydown(event: KeyboardEvent): void {
    if (event.key !== "Escape") {
        return;
    }
    closeMenus();
    closeSidebar();
}

onMounted(() => {
    document.addEventListener("click", onDocumentClick);
    document.addEventListener("keydown", onKeydown);
});

onBeforeUnmount(() => {
    document.removeEventListener("click", onDocumentClick);
    document.removeEventListener("keydown", onKeydown);
});
</script>

<template>
    <!-- Three siblings, so the mounted app *is* the layout's flex row: `#app` is
         that row (display/height/overflow in src/styles/app.css).  Wrapping them in
         another div would leave the sidebar unable to scroll. -->
    <!-- Scrim behind the mobile sidebar drawer -->
    <div :class="['fixed inset-0 z-30 bg-ink-950/60 backdrop-blur-sm lg:hidden',
                  state.sidebarOpen ? '' : 'hidden']"
         @click="closeSidebar()"></div>

    <AppSidebar />

    <!-- Main content panel -->
    <div class="flex-1 flex flex-col h-full overflow-hidden">
        <DetailHeader />
        <main class="flex-1 overflow-hidden p-3 sm:p-6 flex flex-col">
            <template v-if="hasData">
                <SourceView v-if="state.tab === 'code'" />
                <OutputView v-else-if="state.tab === 'output'" />
                <OverviewView v-else />
            </template>
            <EmptyState v-else />
        </main>
    </div>
</template>
