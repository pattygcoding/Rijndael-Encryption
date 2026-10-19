import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// Relative asset URLs, so one build works both at the custom domain's root
// (encryption.pattygcoding.com) and under a `<user>.github.io/<repo>/` path - the
// dashboard derives its own deployment prefix (`APP_DIR`) from wherever the page
// happens to be served.
export default defineConfig({
    base: "./",
    plugins: [vue()],
    build: {
        outDir: "dist",
        emptyOutDir: true,
    },
});
