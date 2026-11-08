# Putting the case study into a site

`build_page.py` makes a page that stands on its own. When the case study belongs in the person's own site (Nuxt, Next.js, Astro, SvelteKit, WordPress), port it instead of embedding the HTML. Search engines and the site's header, footer and theme switch should see it as one of the site's pages.

## If the site already has one

Read an existing interactive case study in the site whole, both its component and its shared stylesheet and behaviour, before writing anything. Copy its structure and only change the content. A repo's `CLAUDE.md` or `AGENTS.md` usually says where they live. One shape that works well, from a Nuxt site:

- `components/CaseStudy/<Project>.vue`: one component per case study, with the content as constants at the top of its script (`kpis`, `facts`, `weeks`, `stages`, `decisions`, `fixes`, `details`, `stack`). Those match `case.json`'s keys.
- `assets/css/case-study.css`: shared by every case study (in Vue, `<style scoped src>`). The project's own colours are a few `--cs-stage-*` overrides in each component.
- `composables/useCaseStudy.ts`: the shared behaviour, which is the progress bar, the figures' count-up, the decision deck (`useCaseDeck()`), the gauge offset and the stack chip colours.
- `pages/portfolio/<slug>.vue`: SEO only (title within 60 characters, description within 160, canonical, Open Graph image, JSON-LD `Article` + `BreadcrumbList`), rendering the component.
- New routes added to the prerender list, the sitemap and `llms.txt`. The project's portfolio card links to the case study instead of a lightbox.

## If it's the first one

1. Build the page with `build_page.py` first and agree on the content with the person. `case.json` is the content model.
2. Make the shared pieces once: copy `scripts/page.css` into the site's stylesheet folder and remap the tokens to the site's own. Keep the `--cs-*` names and point them at the site's variables, so light, dark and any other theme follow the site's switch rather than `prefers-color-scheme`. Then port `scripts/page.js` into the framework's lifecycle (mount and unmount listeners, reactive state for the selected bar, zone, card and side).
3. Make one component per case study from the generated HTML. The classes stay as they are, so the stylesheet keeps working.
4. Replace the built-in lightbox with the site's own if it has one, and the page's buttons with the site's button component if it has one.
5. Raise `--cs-top` to the height of a fixed site header, so the sticky deck sits below it.
6. Prerender the page, and check it in every theme the site has, at phone width, and with reduced motion on.

## Things that bite

- A theme that differs per mode must be done in CSS (classes or tokens), not by rendering one branch. A prerendered page bakes in whichever branch rendered at build time and flashes for everyone else.
- Shared stylesheets imported per component can be cached by file name in some bundlers. If a production build drops styles that work in dev, import the sheet from the script instead.
- Count-up figures render their real values on the server and only animate in the browser. A crawler and a no-JavaScript reader see the real numbers.
