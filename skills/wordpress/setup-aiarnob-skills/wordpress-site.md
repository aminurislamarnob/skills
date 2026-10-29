# WordPress site

The local site this plugin runs on. `plugin-docs`, `browser-walkthrough` and `feature-video` open it and log in; `wp-worktree` clones its database.

- **URL**: `https://example.test`
- **WordPress root**: `/Users/me/Herd/example` (`WP_PATH` for `feature-video`; the directory to run `wp` from)
- **This repo is**: a plugin at `wp-content/plugins/example` | a theme | the whole site

## Logging in

- **Source**: env file | WP-CLI | other
- **Env file**: `tests/e2e/.env` (gitignored), with `WP_BASE_URL`, `WP_USERNAME`, `WP_PASSWORD`. Load it with `set -a; . tests/e2e/.env; set +a`.
- **WP-CLI**: mint a cookie for `<admin-username>` with `wp eval 'echo wp_generate_auth_cookie(<id>, DAY_IN_SECONDS);'` and set it with `document.cookie`.

Never write a password here.

## Other roles

Users a run may need besides the administrator, and where their credentials come from (seed file, e2e helper, WP-CLI):

- **Vendor / shop manager**: `<username>` — from `<source>`
- **Customer**: `<username>` — from `<source>`

## Services the site depends on

Things to start before a run and how to confirm they answer (webhook listener, queue worker, mail catcher):

- `stripe listen --forward-to https://example.test/?wc-api=wc_stripe` — ready when the log prints the webhook secret
