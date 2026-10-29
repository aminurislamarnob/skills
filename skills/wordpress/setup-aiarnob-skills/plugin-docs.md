# Plugin docs

Where the client-facing docs for this plugin live. `plugin-docs` writes here.

- **Docs root**: `docs/` in this repo | `../example-docs` (a sibling repo)
- **Pages**: `<root>/content/docs/<slug>.mdx`, sidebar in `<root>/content/docs/meta.json`
- **Images**: `<root>/public/docs/images/<name>.jpg`, referenced as `/docs/images/<name>.jpg`
- **Build**: `pnpm build` from `<root>` | none
- **Format**: [StoreSuite docs](https://storesuite.dev/docs); voice and page shape per the skill's `STYLE.md`

## Distribution

- **Ships to WordPress.org**: yes | no. When yes, the docs root is listed in `.distignore` so screenshots stay out of the plugin zip.

## Seeded content

Demo content `plugin-docs` created for screenshots and has not yet removed (IDs, post types), so a later run can reuse or clean it up:

- (none yet)
