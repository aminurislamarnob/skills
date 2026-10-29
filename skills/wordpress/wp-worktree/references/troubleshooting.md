# Troubleshooting & Common Issues

## 1. Domain Returns 502 Bad Gateway

- **Cause**: The PHP-FPM socket configured for the site is stopped or mismatched.
- **Fix**: Check `herd status` and ensure PHP-FPM is running:
  ```bash
  herd restart
  ```
  Check the site's PHP version with `wp-worktree status` and ensure it matches an installed Herd PHP version.

## 2. Curl or Fetch Fails with SSL Certificate Error

- **Cause**: Command-line tools (curl, Node.js, Python) may not automatically trust macOS Keychain root certificates used by Laravel Herd.
- **Fix**:
  - In `curl`: Pass `-k` or `--insecure`:
    ```bash
    curl -k -IL https://site--feature.test
    ```
  - In Node / Playwright:
    ```bash
    NODE_TLS_REJECT_UNAUTHORIZED=0 npx playwright test
    ```

## 3. Database Connection Error (Error establishing a database connection)

- **Cause**: MySQL service is down or root password in parent `wp-config.php` differs.
- **Fix**:
  - Test MySQL connectivity directly:
    ```bash
    mysql -u root -proot -e "SHOW DATABASES;"
    ```
  - If Herd Pro services are used, ensure MySQL service is running via `herd services:list`.

## 4. "Cannot create worktree: branch already exists"

- **Cause**: A branch with the same name was created previously.
- **Fix**: Either choose a new name or delete the stale branch:
  ```bash
  git branch -D <branch-name>
  wp-worktree create <branch-name>
  ```

## 5. Cleaning Stale Worktrees

If an ephemeral directory or worktree checkout was manually deleted:
```bash
# Clean up git worktree pruning
git worktree prune

# Remove orphaned entry from registry
wp-worktree remove <worktree-name> --force
```
