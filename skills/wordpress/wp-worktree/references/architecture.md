# Worktree Architecture & Herd Mechanics

This document explains the internal design of `wp-worktree` and how it coordinates WordPress, Git Worktrees, and Laravel Herd.

## Overview

When developing with AI agents in parallel, each agent needs:
1. An isolated checkout of the code (provided by git worktrees).
2. A distinct web URL to test changes in a real browser or HTTP client.
3. An isolated database to run schema changes or store test data without corrupting other agent sessions.

## Directory Topology

### Plugin / Theme Repositories (Nested inside WordPress)

In typical WordPress setups (e.g. `~/Herd/woocommerce/wp-content/plugins/my-plugin`):
```
~/Herd/woocommerce/                            <-- Main WordPress Installation
├── wp-content/
│   ├── plugins/
│   │   ├── my-plugin/                        <-- Main Git Repo
│   │   │   └── .claude/worktrees/agent-1     <-- Git Worktree 1
│   │   └── my-plugin--feat-cart/             <-- Git Worktree 2

~/.herd-worktrees/
├── woocommerce--agent-1/                     <-- Ephemeral Herd Site 1
│   ├── wp-admin/ -> ~/Herd/woocommerce/wp-admin
│   ├── wp-includes/ -> ~/Herd/woocommerce/wp-includes
│   ├── wp-content/
│   │   ├── themes/ -> ~/Herd/woocommerce/wp-content/themes
│   │   ├── uploads/ -> ~/Herd/woocommerce/wp-content/uploads
│   │   └── plugins/
│   │       ├── other-plugins -> ~/Herd/woocommerce/wp-content/plugins/*
│   │       └── my-plugin -> .../my-plugin/.claude/worktrees/agent-1
│   └── wp-config.php (Isolated DB & dynamic domain)
```

### Full WordPress Site Repositories

When the entire WordPress root is the git repository:
```
~/Herd/my-wp-site/                            <-- Main Repo & Main Site
~/.herd-worktrees/my-wp-site--feat-x/         <-- Git Worktree Checkout & Herd Site
```
The checkout itself contains all WordPress files, so `wp-worktree` directly links and configures it.

## Herd Dynamic Routing & Valet Integration

Laravel Herd uses Nginx and dnsmasq:
1. `herd link <name>` creates a symlink in `~/Library/Application Support/Herd/config/valet/Sites/<name>` pointing to the ephemeral site folder.
2. Herd automatically resolves `http://<name>.test` to `127.0.0.1`.
3. `herd secure <name>` signs a local SSL certificate using Herd's root CA and provisions an isolated Nginx server block for `https://<name>.test`.
4. `herd isolate <php-version>` links the site to the matching PHP-FPM socket (`herd83.sock`, etc.).

## Dynamic WordPress URLs

WordPress stores `siteurl` and `home` options in the database. When an ephemeral site is booted on `https://site--worktree.test`, WordPress would normally redirect to the parent domain.

To prevent this, `wp-worktree` generates a custom `wp-config.php` injecting dynamic URL definitions before `wp-settings.php`:

```php
$worktree_domain = 'site--worktree.test';
if ( defined( 'WP_CLI' ) && WP_CLI ) {
    define( 'WP_HOME', 'https://' . $worktree_domain );
    define( 'WP_SITEURL', 'https://' . $worktree_domain );
} else {
    $http_host = $_SERVER['HTTP_HOST'] ?? $worktree_domain;
    $scheme = ( ! empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off' ) ? 'https' : 'http';
    define( 'WP_HOME', $scheme . '://' . $http_host );
    define( 'WP_SITEURL', $scheme . '://' . $http_host );
    define( 'COOKIE_DOMAIN', $http_host );
}
```

This guarantees:
- Browser requests keep the user on the worktree domain.
- WP-CLI executions correctly set the internal site URL constants.
- Cookies and session storage remain isolated between domains.
