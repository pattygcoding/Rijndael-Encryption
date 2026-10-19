# Rijndael Encryption by Patrick Goodwin

Some of my Rijndael encryption examples in many different programming languages. All are available in 128, 192, and 256 bit examples.

## Showcase dashboard

`src/` is a Vue 3 + TypeScript app built by Vite: a fully client-side dashboard
(no backend, no live compilers) with a sidebar of every implementation and a main
panel whose tabs are **Source Code** and **Overview**. It also has a language
search box, and Category and Key size filters.

Every implementation has its own address, `/<language>-<bits>` — `/c-128`,
`/csharp-256`, `/python-cryptography` — and the sidebar entries are real links, so
they can be copied, bookmarked or opened in a new tab. The site root opens the C
128-bit example, the reference walkthrough (`DEFAULT_IMPL_ID` in
`src/store/data.ts`). The Overview tab carries its own address, e.g.
`/csharp-256/overview`.

```sh
npm install        # once
npm start          # regenerate the data, then serve the dashboard on :5173
npm run build      # regenerate the data, type-check, and write dist/
npm run preview    # serve the built dist/
npm run data       # only regenerate public/encryption-data.js
npm run typecheck  # vue-tsc --noEmit
```

`tools/generate-data.mjs` reads the real `<Language>/<bits>bit/Rijndael<ext>`
files (plus `Python/rijndael.py`), records each file's mode and library, and
writes `public/encryption-data.js`. `npm start` and `npm run build` run it first,
so a new implementation shows up without editing the app. Every generated entry
links back to its exact folder on GitHub (`C#` is URL-encoded as `C%23`).

The published site lives at **<https://encryption.pattygcoding.com/>**.

### Deploying to GitHub Pages

`.github/workflows/deploy.yml` runs on every push to `main`: it installs Node 22,
runs `npm ci` and `npm run build`, uploads `dist/` as the Pages artifact and
publishes it. Pages must be set to publish from **GitHub Actions** (not from a
branch), and the custom domain is a repository setting:

```sh
gh api -X POST repos/pattygcoding/Rijndael-Encryption/pages -f build_type=workflow
gh api -X PUT repos/pattygcoding/Rijndael-Encryption/pages \
    -f cname=encryption.pattygcoding.com
```

The DNS side is a single record at the domain's provider:

```
encryption   CNAME   pattygcoding.github.io
```

If the provider proxies traffic (Cloudflare does by default), switch that record
to **DNS only** (grey cloud); a proxied record breaks Pages' certificate checks.

Pages has no rewrite rules, so the tracked `public/404.html` stands in for them:
it is served for any path it cannot find and rebuilds the request as
`index.html?lang=<id>&tab=<tab>`, so `/csharp-256` and `/csharp-256/overview`
work when opened directly. The dashboard then puts the pretty path back with the
History API. The app derives its deployment prefix at load (`APP_DIR` in
`src/store/session.ts`), so the same build also works under a
`<user>.github.io/<repo>/` path.
