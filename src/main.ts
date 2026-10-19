import { createApp } from "vue";
import App from "./App.vue";
import { configurePrism } from "./prism";
import { APP_DIR, initSession } from "./store/session";
import { initTheme } from "./store/theme";
import "./styles/app.css";

// The built page rewrites public asset URLs to `./logo.svg`, which a deep address
// (`/csharp-256/overview`) would resolve below the deployment root.  Pinning the
// icon to the root keeps every route on the same file.
for (const icon of document.querySelectorAll<HTMLLinkElement>('link[rel="icon"]')) {
    icon.href = APP_DIR + "logo.svg";
}

// The 404.html shim parks a hop counter in sessionStorage so a junk path cannot
// redirect in circles.  Reaching the app means the trip worked, so clear it and
// leave the next bad link free to try again.
try {
    sessionStorage.removeItem("re-404");
} catch {
    // private mode: the shim degrades to showing its own link
}

initTheme();
configurePrism();
initSession();

createApp(App).mount("#app");
