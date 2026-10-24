#!/usr/bin/env bash
# ==============================================================================
# wp-worktree: WordPress + Git Worktree + Herd Multi-Agent Environment Orchestrator
# ==============================================================================
# Enables running multiple WordPress worktrees concurrently on isolated Herd
# domains with database clones and automated WP-CLI wiring for AI agents.
# ==============================================================================

set -eo pipefail

WORKTREE_BASE_DIR="${HOME}/.herd-worktrees"
REGISTRY_FILE="${WORKTREE_BASE_DIR}/registry.json"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Helper for logging
log_info() { printf "%b[wp-worktree]%b %s\n" "${CYAN}" "${NC}" "$1"; }
log_success() { printf "%b[wp-worktree] ✓%b %s\n" "${GREEN}" "${NC}" "$1"; }
log_warn() { printf "%b[wp-worktree] ⚠%b %s\n" "${YELLOW}" "${NC}" "$1"; }
log_error() { printf "%b[wp-worktree] ✗%b %s\n" "${RED}" "${NC}" "$1" >&2; }

init_registry() {
    mkdir -p "${WORKTREE_BASE_DIR}"
    if [ ! -f "${REGISTRY_FILE}" ]; then
        echo "[]" > "${REGISTRY_FILE}"
    fi
}

# ------------------------------------------------------------------------------
# Topology & Environment Detection
# ------------------------------------------------------------------------------
detect_context() {
    local start_dir="${1:-$(pwd)}"
    
    # Check if we are inside a git repository
    if ! git -C "${start_dir}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        log_error "Not inside a git repository: ${start_dir}"
        return 1
    fi

    CURRENT_GIT_ROOT="$(git -C "${start_dir}" rev-parse --show-toplevel)"
    GIT_COMMON_DIR="$(git -C "${start_dir}" rev-parse --git-common-dir)"
    
    # Resolve main git repo root (handles worktrees and submodules)
    if [ -d "${GIT_COMMON_DIR}" ]; then
        if [[ "${GIT_COMMON_DIR}" == /* ]]; then
            MAIN_GIT_ROOT="$(cd "${GIT_COMMON_DIR}/.." && pwd)"
        else
            MAIN_GIT_ROOT="$(cd "${start_dir}/${GIT_COMMON_DIR}/.." && pwd)"
        fi
        # If git common dir was just .git inside the repo
        if [ ! -d "${MAIN_GIT_ROOT}" ] || [ "${MAIN_GIT_ROOT}" = "/" ]; then
            MAIN_GIT_ROOT="${CURRENT_GIT_ROOT}"
        fi
    else
        MAIN_GIT_ROOT="${CURRENT_GIT_ROOT}"
    fi

    # Detect current branch
    CURRENT_BRANCH="$(git -C "${start_dir}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")"

    # Search upwards from MAIN_GIT_ROOT for WordPress installation (wp-config.php and wp-load.php)
    local check_dir="${MAIN_GIT_ROOT}"
    WP_ROOT=""
    while [ "${check_dir}" != "/" ] && [ -n "${check_dir}" ]; do
        if [ -f "${check_dir}/wp-load.php" ] && [ -f "${check_dir}/wp-config.php" ]; then
            WP_ROOT="${check_dir}"
            break
        fi
        check_dir="$(dirname "${check_dir}")"
    done

    # If WP_ROOT not found upwards, check if current root is full WP site
    if [ -z "${WP_ROOT}" ]; then
        if [ -f "${CURRENT_GIT_ROOT}/wp-load.php" ] && [ -f "${CURRENT_GIT_ROOT}/wp-config.php" ]; then
            WP_ROOT="${CURRENT_GIT_ROOT}"
        fi
    fi

    if [ -z "${WP_ROOT}" ]; then
        # Check if parent parameter was supplied
        if [ -n "${OPT_PARENT_WP}" ] && [ -f "${OPT_PARENT_WP}/wp-config.php" ]; then
            WP_ROOT="${OPT_PARENT_WP}"
        else
            log_error "Could not find a parent WordPress installation (with wp-config.php and wp-load.php)."
            log_error "Please run inside a WordPress site/plugin/theme repo or pass --parent=/path/to/wordpress"
            return 1
        fi
    fi

    # Classify kind: plugin, theme, or full site
    REPO_KIND="unknown"
    TARGET_SLUG=""
    if [ "${MAIN_GIT_ROOT}" = "${WP_ROOT}" ] || [ "${CURRENT_GIT_ROOT}" = "${WP_ROOT}" ]; then
        REPO_KIND="site"
        TARGET_SLUG="$(basename "${WP_ROOT}")"
    elif [[ "${MAIN_GIT_ROOT}" == "${WP_ROOT}/wp-content/plugins/"* ]]; then
        REPO_KIND="plugin"
        TARGET_SLUG="$(basename "${MAIN_GIT_ROOT}")"
    elif [[ "${MAIN_GIT_ROOT}" == "${WP_ROOT}/wp-content/themes/"* ]]; then
        REPO_KIND="theme"
        TARGET_SLUG="$(basename "${MAIN_GIT_ROOT}")"
    else
        # Fallback: inspect path relative to WP_ROOT
        local rel_path="${MAIN_GIT_ROOT#"${WP_ROOT}/"}"
        if [[ "${rel_path}" == wp-content/plugins/* ]]; then
            REPO_KIND="plugin"
            TARGET_SLUG="$(echo "${rel_path}" | awk -F'/' '{print $3}')"
        elif [[ "${rel_path}" == wp-content/themes/* ]]; then
            REPO_KIND="theme"
            TARGET_SLUG="$(echo "${rel_path}" | awk -F'/' '{print $3}')"
        else
            REPO_KIND="site"
            TARGET_SLUG="$(basename "${MAIN_GIT_ROOT}")"
        fi
    fi

    # Determine Parent Herd Site Name
    PARENT_SITE_NAME="$(basename "${WP_ROOT}")"
    PARENT_DOMAIN="${PARENT_SITE_NAME}.test"

    # Detect Herd isolated PHP version for parent site if any
    PARENT_PHP_VERSION=""
    if command -v herd >/dev/null 2>&1; then
        PARENT_PHP_VERSION="$(herd site:info "${PARENT_SITE_NAME}" 2>/dev/null | grep -E "^PHP:" | awk '{print $2}' || true)"
    fi
}

# ------------------------------------------------------------------------------
# Extract Database Credentials from wp-config.php
# ------------------------------------------------------------------------------
parse_wp_config() {
    local config_file="$1"
    if [ ! -f "${config_file}" ]; then
        log_error "Configuration file not found: ${config_file}"
        return 1
    fi

    CONFIG_JSON="$(php -r '
        $f = $argv[1];
        $c = file_get_contents($f);
        preg_match("/define\s*\(\s*[\x27\x22]DB_NAME[\x27\x22]\s*,\s*[\x27\x22]([^\x27\x22]+)[\x27\x22]\s*\)/", $c, $m1);
        preg_match("/define\s*\(\s*[\x27\x22]DB_USER[\x27\x22]\s*,\s*[\x27\x22]([^\x27\x22]+)[\x27\x22]\s*\)/", $c, $m2);
        preg_match("/define\s*\(\s*[\x27\x22]DB_PASSWORD[\x27\x22]\s*,\s*[\x27\x22]([^\x27\x22]*)[\x27\x22]\s*\)/", $c, $m3);
        preg_match("/define\s*\(\s*[\x27\x22]DB_HOST[\x27\x22]\s*,\s*[\x27\x22]([^\x27\x22]+)[\x27\x22]\s*\)/", $c, $m4);
        preg_match("/\\\$table_prefix\s*=\s*[\x27\x22]([^\x27\x22]+)[\x27\x22]/", $c, $m5);
        echo json_encode([
            "db_name" => $m1[1] ?? "wordpress",
            "db_user" => $m2[1] ?? "root",
            "db_pass" => $m3[1] ?? "",
            "db_host" => $m4[1] ?? "localhost",
            "table_prefix" => $m5[1] ?? "wp_"
        ]);
    ' "${config_file}")"

    PARENT_DB_NAME="$(echo "${CONFIG_JSON}" | php -r 'echo json_decode(file_get_contents("php://stdin"), true)["db_name"];')"
    PARENT_DB_USER="$(echo "${CONFIG_JSON}" | php -r 'echo json_decode(file_get_contents("php://stdin"), true)["db_user"];')"
    PARENT_DB_PASS="$(echo "${CONFIG_JSON}" | php -r 'echo json_decode(file_get_contents("php://stdin"), true)["db_pass"];')"
    PARENT_DB_HOST="$(echo "${CONFIG_JSON}" | php -r 'echo json_decode(file_get_contents("php://stdin"), true)["db_host"];')"
    PARENT_DB_PREFIX="$(echo "${CONFIG_JSON}" | php -r 'echo json_decode(file_get_contents("php://stdin"), true)["table_prefix"];')"
}

# ------------------------------------------------------------------------------
# Sanitize worktree names for URLs and MySQL DB names
# ------------------------------------------------------------------------------
sanitize_name() {
    local input="$1"
    # Convert to lowercase, replace non-alphanumeric with dash
    echo "${input}" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9_-]+/-/g' | sed -E 's/^-+|-+$//g' | cut -c1-30
}

sanitize_db_name() {
    local input="$1"
    # MySQL identifiers: alphanumeric and underscore, max 64 chars
    echo "${input}" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9_]+/_/g' | sed -E 's/^_+|_+$//g' | cut -c1-60
}

# ------------------------------------------------------------------------------
# Clone or Setup Database
# ------------------------------------------------------------------------------
setup_database() {
    local db_mode="$1"
    local source_db="$2"
    local target_db="$3"
    local host="$4"
    local user="$5"
    local pass="$6"

    if [ "${db_mode}" = "shared" ]; then
        log_info "Using shared parent database: ${source_db}"
        return 0
    fi

    log_info "Creating database [${target_db}] on MySQL..."
    local mysql_auth=(-h "${host}" -u "${user}")
    if [ -n "${pass}" ]; then
        mysql_auth+=("-p${pass}")
    fi

    mysql "${mysql_auth[@]}" -e "CREATE DATABASE IF NOT EXISTS \`${target_db}\`;"

    if [ "${db_mode}" = "clone" ]; then
        log_info "Cloning tables and data from [${source_db}] to [${target_db}]..."
        mysqldump "${mysql_auth[@]}" --single-transaction --quick "${source_db}" | mysql "${mysql_auth[@]}" "${target_db}"
        log_success "Database cloned successfully."
    elif [ "${db_mode}" = "empty" ]; then
        log_info "Empty database [${target_db}] created."
    fi
}

# ------------------------------------------------------------------------------
# Generate Ephemeral WordPress Site (Herd Document Root)
# ------------------------------------------------------------------------------
build_ephemeral_site() {
    local worktree_dir="$1"
    local ephemeral_dir="$2"
    local domain="$3"
    local target_db="$4"

    mkdir -p "${ephemeral_dir}"

    if [ "${REPO_KIND}" = "site" ]; then
        # For full site repositories, worktree is already the full WordPress install
        log_info "Full site repository detected; linking worktree directory directly."
        # If worktree_dir is different from ephemeral_dir, symlink or use directly
        if [ "${worktree_dir}" != "${ephemeral_dir}" ]; then
            rm -rf "${ephemeral_dir}"
            ln -s "${worktree_dir}" "${ephemeral_dir}"
        fi
        
        # Ensure wp-config-local.php or custom wp-config handles dynamic domain and isolated DB
        generate_wp_config "${WP_ROOT}/wp-config.php" "${worktree_dir}/wp-config.php" "${domain}" "${target_db}"
        return 0
    fi

    log_info "Constructing isolated WordPress core environment at ${ephemeral_dir}..."

    # 1. Symlink core WordPress root files (index.php, wp-load.php, wp-login.php, etc.)
    for file in "${WP_ROOT}"/*.php; do
        if [ -f "${file}" ]; then
            local fname
            fname="$(basename "${file}")"
            if [ "${fname}" != "wp-config.php" ]; then
                ln -sf "${file}" "${ephemeral_dir}/${fname}"
            fi
        fi
    done

    # 2. Symlink core admin and includes directories
    ln -sf "${WP_ROOT}/wp-admin" "${ephemeral_dir}/wp-admin"
    ln -sf "${WP_ROOT}/wp-includes" "${ephemeral_dir}/wp-includes"

    # 3. Create isolated wp-content structure
    mkdir -p "${ephemeral_dir}/wp-content"
    
    # Symlink uploads, themes, languages
    if [ -d "${WP_ROOT}/wp-content/uploads" ]; then
        ln -sf "${WP_ROOT}/wp-content/uploads" "${ephemeral_dir}/wp-content/uploads"
    fi
    if [ -d "${WP_ROOT}/wp-content/languages" ]; then
        ln -sf "${WP_ROOT}/wp-content/languages" "${ephemeral_dir}/wp-content/languages"
    fi

    # Handle themes
    if [ "${REPO_KIND}" = "theme" ]; then
        mkdir -p "${ephemeral_dir}/wp-content/themes"
        for t in "${WP_ROOT}/wp-content/themes"/*; do
            if [ -d "${t}" ] && [ "$(basename "${t}")" != "${TARGET_SLUG}" ]; then
                ln -sf "${t}" "${ephemeral_dir}/wp-content/themes/$(basename "${t}")"
            fi
        done
        ln -sfn "${worktree_dir}" "${ephemeral_dir}/wp-content/themes/${TARGET_SLUG}"
    else
        ln -sf "${WP_ROOT}/wp-content/themes" "${ephemeral_dir}/wp-content/themes"
    fi

    # Handle plugins
    mkdir -p "${ephemeral_dir}/wp-content/plugins"
    for p in "${WP_ROOT}/wp-content/plugins"/*; do
        if [ -e "${p}" ]; then
            local pname
            pname="$(basename "${p}")"
            if [ "${pname}" != "${TARGET_SLUG}" ]; then
                ln -sf "${p}" "${ephemeral_dir}/wp-content/plugins/${pname}"
            fi
        fi
    done

    # Map the worktree as the target plugin!
    if [ "${REPO_KIND}" = "plugin" ]; then
        ln -sfn "${worktree_dir}" "${ephemeral_dir}/wp-content/plugins/${TARGET_SLUG}"
        log_success "Mapped plugin [${TARGET_SLUG}] worktree -> wp-content/plugins/${TARGET_SLUG}"
    fi

    # 4. Generate isolated wp-config.php
    generate_wp_config "${WP_ROOT}/wp-config.php" "${ephemeral_dir}/wp-config.php" "${domain}" "${target_db}"
}

generate_wp_config() {
    local source_config="$1"
    local dest_config="$2"
    local domain="$3"
    local target_db="$4"

    log_info "Generating isolated wp-config.php with dynamic domain and DB isolation..."

    php -r '
        $source = $argv[1];
        $dest = $argv[2];
        $domain = $argv[3];
        $targetDb = $argv[4];

        $content = file_get_contents($source);

        // Replace DB_NAME definition
        $content = preg_replace(
            "/define\s*\(\s*([\x27\x22])DB_NAME([\x27\x22])\s*,\s*([\x27\x22])[^\x27\x22]+([\x27\x22])\s*\);/",
            "define($1DB_NAME$2, $3" . $targetDb . "$4);",
            $content
        );

        // Remove any existing WP_HOME or WP_SITEURL definitions to avoid conflicts
        $content = preg_replace("/define\s*\(\s*[\x27\x22]WP_HOME[\x27\x22][^;]+;/", "", $content);
        $content = preg_replace("/define\s*\(\s*[\x27\x22]WP_SITEURL[\x27\x22][^;]+;/", "", $content);
        $content = preg_replace("/define\s*\(\s*[\x27\x22]COOKIE_DOMAIN[\x27\x22][^;]+;/", "", $content);

        // Inject dynamic URL resolution right before wp-settings.php include
        $injection = "
// --- [wp-worktree] Dynamic Domain Resolution ---
\$worktree_domain = \x27" . $domain . "\x27;
if ( defined( \x27WP_CLI\x27 ) && WP_CLI ) {
    define( \x27WP_HOME\x27, \x27https://\x27 . \$worktree_domain );
    define( \x27WP_SITEURL\x27, \x27https://\x27 . \$worktree_domain );
} else {
    \$http_host = \$_SERVER[\x27HTTP_HOST\x27] ?? \$worktree_domain;
    \$scheme = ( ! empty(\$_SERVER[\x27HTTPS\x27]) && \$_SERVER[\x27HTTPS\x27] !== \x27off\x27 ) ? \x27https\x27 : \x27http\x27;
    define( \x27WP_HOME\x27, \$scheme . \x27://\x27 . \$http_host );
    define( \x27WP_SITEURL\x27, \$scheme . \x27://\x27 . \$http_host );
    define( \x27COOKIE_DOMAIN\x27, \$http_host );
}
if ( ! defined( \x27WP_ENVIRONMENT_TYPE\x27 ) ) {
    define( \x27WP_ENVIRONMENT_TYPE\x27, \x27local\x27 );
}
// --- [/wp-worktree] ---

";

        if (strpos($content, "require_once ABSPATH . \x27wp-settings.php\x27;") !== false) {
            $content = str_replace(
                "require_once ABSPATH . \x27wp-settings.php\x27;",
                $injection . "require_once ABSPATH . \x27wp-settings.php\x27;",
                $content
            );
        } else {
            $content .= "\n" . $injection;
        }

        file_put_contents($dest, $content);
    ' "${source_config}" "${dest_config}" "${domain}" "${target_db}"
}

# ------------------------------------------------------------------------------
# Register Site in Herd & Secure with SSL
# ------------------------------------------------------------------------------
wire_herd_site() {
    local site_path="$1"
    local site_name="$2"
    local php_ver="$3"

    log_info "Linking site [${site_name}] into Herd..."
    (cd "${site_path}" && herd link "${site_name}")

    log_info "Securing [${site_name}.test] with local SSL..."
    (cd "${site_path}" && herd secure "${site_name}")

    if [ -n "${php_ver}" ] && [ "${php_ver}" != "default" ]; then
        log_info "Isolating PHP version [${php_ver}] to match parent..."
        (cd "${site_path}" && herd isolate "${php_ver}" || true)
    fi
}

# ------------------------------------------------------------------------------
# Wire WP-CLI inside Worktree & Git Guardrails
# ------------------------------------------------------------------------------
wire_worktree_environment() {
    local worktree_dir="$1"
    local ephemeral_dir="$2"
    local metadata_json="$3"

    # 1. Write wp-cli.local.yml inside the worktree so `wp` works natively
    log_info "Wiring WP-CLI configuration (wp-cli.local.yml) inside worktree..."
    cat > "${worktree_dir}/wp-cli.local.yml" <<EOF
# Automatically generated by wp-worktree
path: "${ephemeral_dir}"
EOF

    # 2. Save metadata inside worktree
    echo "${metadata_json}" > "${worktree_dir}/.worktree-meta.json"

    # 3. Add to git local exclude so worktree configs are NEVER committed
    local git_dir
    git_dir="$(git -C "${worktree_dir}" rev-parse --git-dir 2>/dev/null || echo "")"
    if [ -n "${git_dir}" ] && [ -d "${git_dir}/info" ]; then
        local exclude_file="${git_dir}/info/exclude"
        if ! grep -q "wp-cli.local.yml" "${exclude_file}" 2>/dev/null; then
            echo "wp-cli.local.yml" >> "${exclude_file}"
            echo ".worktree-meta.json" >> "${exclude_file}"
            log_success "Added worktree config files to git local exclude (.git/info/exclude)."
        fi
    fi
}

# ------------------------------------------------------------------------------
# Update Registry
# ------------------------------------------------------------------------------
save_to_registry() {
    local metadata_json="$1"
    init_registry

    php -r '
        $regFile = $argv[1];
        $entry = json_decode($argv[2], true);
        $data = json_decode(file_get_contents($regFile), true) ?: [];

        // Remove any existing entry with same id
        $filtered = array_values(array_filter($data, function($item) use ($entry) {
            return ($item["id"] ?? "") !== $entry["id"];
        }));

        $filtered[] = $entry;
        file_put_contents($regFile, json_encode($filtered, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));
    ' "${REGISTRY_FILE}" "${metadata_json}"
}

remove_from_registry() {
    local id="$1"
    init_registry

    php -r '
        $regFile = $argv[1];
        $id = $argv[2];
        $data = json_decode(file_get_contents($regFile), true) ?: [];

        $filtered = array_values(array_filter($data, function($item) use ($id) {
            return ($item["id"] ?? "") !== $id && ($item["name"] ?? "") !== $id;
        }));

        file_put_contents($regFile, json_encode($filtered, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));
    ' "${REGISTRY_FILE}" "${id}"
}

# ------------------------------------------------------------------------------
# COMMAND: setup (Adopts an existing worktree, e.g. .claude/worktrees/*)
# ------------------------------------------------------------------------------
cmd_setup() {
    local target_dir="${1:-$(pwd)}"
    detect_context "${target_dir}"
    parse_wp_config "${WP_ROOT}/wp-config.php"

    local raw_name="${OPT_NAME:-}"
    if [ -z "${raw_name}" ]; then
        raw_name="$(basename "${CURRENT_GIT_ROOT}")"
        # If in .claude/worktrees/<hash>, use the hash or branch
        if [ "${raw_name}" = "worktrees" ] || [[ "${CURRENT_GIT_ROOT}" == *".claude/worktrees"* ]]; then
            raw_name="$(basename "${CURRENT_GIT_ROOT}")"
        fi
    fi

    local clean_name
    clean_name="$(sanitize_name "${raw_name}")"
    local herd_site_name="${PARENT_SITE_NAME}--${clean_name}"
    local domain="${herd_site_name}.test"
    local ephemeral_dir="${WORKTREE_BASE_DIR}/${herd_site_name}"

    local db_mode="${OPT_DB:-clone}"
    local target_db
    if [ "${db_mode}" = "shared" ]; then
        target_db="${PARENT_DB_NAME}"
    else
        local clean_db_suffix
        clean_db_suffix="$(sanitize_db_name "${clean_name}")"
        target_db="${PARENT_DB_NAME}_wt_${clean_db_suffix}"
    fi

    log_info "Setting up worktree environment for [${clean_name}]..."
    log_info "Parent WordPress: ${WP_ROOT} (${PARENT_SITE_NAME})"
    log_info "Repo Kind: ${REPO_KIND} (${TARGET_SLUG})"
    log_info "Domain: https://${domain}"
    log_info "Database Mode: ${db_mode} (${target_db})"

    # 1. Setup Database
    setup_database "${db_mode}" "${PARENT_DB_NAME}" "${target_db}" "${PARENT_DB_HOST}" "${PARENT_DB_USER}" "${PARENT_DB_PASS}"

    # 2. Build ephemeral WordPress environment
    build_ephemeral_site "${CURRENT_GIT_ROOT}" "${ephemeral_dir}" "${domain}" "${target_db}"

    # 3. Search and replace domain in DB if cloned
    if [ "${db_mode}" = "clone" ]; then
        log_info "Updating URLs in cloned database from https://${PARENT_DOMAIN} to https://${domain}..."
        (cd "${ephemeral_dir}" && wp search-replace "https://${PARENT_DOMAIN}" "https://${domain}" --all-tables --skip-plugins --skip-themes --quiet || true)
        (cd "${ephemeral_dir}" && wp search-replace "http://${PARENT_DOMAIN}" "https://${domain}" --all-tables --skip-plugins --skip-themes --quiet || true)
    fi

    # 4. Wire Herd
    wire_herd_site "${ephemeral_dir}" "${herd_site_name}" "${PARENT_PHP_VERSION}"

    # 5. Metadata and WP-CLI
    local metadata_json
    metadata_json="$(php -r '
        echo json_encode([
            "id" => $argv[1],
            "name" => $argv[2],
            "branch" => $argv[3],
            "parent_site" => $argv[4],
            "parent_wp_path" => $argv[5],
            "site_path" => $argv[6],
            "worktree_path" => $argv[7],
            "kind" => $argv[8],
            "slug" => $argv[9],
            "domain" => $argv[10],
            "url" => "https://" . $argv[10],
            "db_mode" => $argv[11],
            "db_name" => $argv[12],
            "created_at" => date("c")
        ], JSON_UNESCAPED_SLASHES);
    ' "${herd_site_name}" "${clean_name}" "${CURRENT_BRANCH}" "${PARENT_SITE_NAME}" "${WP_ROOT}" "${ephemeral_dir}" "${CURRENT_GIT_ROOT}" "${REPO_KIND}" "${TARGET_SLUG}" "${domain}" "${db_mode}" "${target_db}")"

    wire_worktree_environment "${CURRENT_GIT_ROOT}" "${ephemeral_dir}" "${metadata_json}"
    save_to_registry "${metadata_json}"

    printf "\n"
    log_success "WordPress worktree environment ready!"
    printf "%b------------------------------------------------------------%b\n" "${BOLD}" "${NC}"
    printf "  %bURL:%b          https://%s\n" "${BOLD}" "${NC}" "${domain}"
    printf "  %bAdmin:%b        https://%s/wp-admin/\n" "${BOLD}" "${NC}" "${domain}"
    printf "  %bDatabase:%b     %s (%s)\n" "${BOLD}" "${NC}" "${target_db}" "${db_mode}"
    printf "  %bHerd Site:%b    %s\n" "${BOLD}" "${NC}" "${herd_site_name}"
    printf "  %bWorktree:%b     %s\n" "${BOLD}" "${NC}" "${CURRENT_GIT_ROOT}"
    printf "  %bWP-CLI:%b       Pre-configured! Run 'wp <cmd>' in this directory.\n" "${BOLD}" "${NC}"
    printf "%b------------------------------------------------------------%b\n\n" "${BOLD}" "${NC}"
}

# ------------------------------------------------------------------------------
# COMMAND: create (Creates git worktree + wires Herd & DB)
# ------------------------------------------------------------------------------
cmd_create() {
    local raw_name="$1"
    if [ -z "${raw_name}" ]; then
        log_error "Missing worktree/branch name. Usage: wp-worktree create <name> [--from=<base>]"
        return 1
    fi

    detect_context "$(pwd)"
    local clean_name
    clean_name="$(sanitize_name "${raw_name}")"

    local base_commit="${OPT_FROM:-HEAD}"
    local worktree_dest

    # Determine worktree destination
    if [ -d "${MAIN_GIT_ROOT}/.claude/worktrees" ]; then
        worktree_dest="${MAIN_GIT_ROOT}/.claude/worktrees/${clean_name}"
    else
        worktree_dest="${MAIN_GIT_ROOT}/../${TARGET_SLUG}--${clean_name}"
    fi

    log_info "Creating git worktree [${clean_name}] at ${worktree_dest}..."
    if [ -d "${worktree_dest}" ]; then
        log_warn "Directory ${worktree_dest} already exists. Using existing worktree..."
    else
        git -C "${MAIN_GIT_ROOT}" worktree add -B "${clean_name}" "${worktree_dest}" "${base_commit}"
    fi

    # Now setup the worktree environment
    OPT_NAME="${clean_name}"
    cmd_setup "${worktree_dest}"
}

# ------------------------------------------------------------------------------
# COMMAND: list
# ------------------------------------------------------------------------------
cmd_list() {
    init_registry

    if [ "${OPT_JSON:-false}" = "true" ]; then
        cat "${REGISTRY_FILE}"
        return 0
    fi

    php -r '
        $regFile = $argv[1];
        $data = json_decode(file_get_contents($regFile), true) ?: [];

        if (empty($data)) {
            echo "No active WordPress worktrees found.\n";
            exit(0);
        }

        echo "\nActive WordPress Worktrees:\n";
        printf("%-30s | %-32s | %-20s | %-10s\n", "Worktree / Branch", "Domain", "Database", "Kind");
        echo str_repeat("-", 100) . "\n";

        foreach ($data as $item) {
            printf(
                "%-30s | %-32s | %-20s | %-10s\n",
                substr($item["name"] . " (" . $item["branch"] . ")", 0, 30),
                $item["domain"],
                $item["db_name"] . " [" . $item["db_mode"] . "]",
                $item["kind"] . ":" . $item["slug"]
            );
        }
        echo "\n";
    ' "${REGISTRY_FILE}"
}

# ------------------------------------------------------------------------------
# COMMAND: url
# ------------------------------------------------------------------------------
cmd_url() {
    local target="$1"
    init_registry

    if [ -z "${target}" ]; then
        if [ -f ".worktree-meta.json" ]; then
            php -r 'echo json_decode(file_get_contents(".worktree-meta.json"), true)["url"] . "\n";'
            return 0
        fi
        log_error "No worktree specified and current directory is not an active worktree."
        return 1
    fi

    php -r '
        $regFile = $argv[1];
        $target = $argv[2];
        $data = json_decode(file_get_contents($regFile), true) ?: [];

        foreach ($data as $item) {
            if ($item["id"] === $target || $item["name"] === $target || $item["domain"] === $target) {
                echo $item["url"] . "\n";
                exit(0);
            }
        }
        exit(1);
    ' "${REGISTRY_FILE}" "${target}"
}

# ------------------------------------------------------------------------------
# COMMAND: status
# ------------------------------------------------------------------------------
cmd_status() {
    local target="$1"
    local meta_file=""

    if [ -n "${target}" ]; then
        init_registry
        local site_path
        site_path="$(php -r '
            $reg = json_decode(file_get_contents($argv[1]), true) ?: [];
            foreach ($reg as $item) {
                if ($item["id"] === $argv[2] || $item["name"] === $argv[2]) {
                    echo $item["worktree_path"];
                    exit(0);
                }
            }
        ' "${REGISTRY_FILE}" "${target}")"
        if [ -n "${site_path}" ] && [ -f "${site_path}/.worktree-meta.json" ]; then
            meta_file="${site_path}/.worktree-meta.json"
        fi
    elif [ -f ".worktree-meta.json" ]; then
        meta_file=".worktree-meta.json"
    fi

    if [ -z "${meta_file}" ] || [ ! -f "${meta_file}" ]; then
        log_error "No active worktree metadata found for status check."
        return 1
    fi

    php -r '
        $meta = json_decode(file_get_contents($argv[1]), true);
        echo "Worktree Status: " . $meta["name"] . "\n";
        echo "  URL:           " . $meta["url"] . "\n";
        echo "  Parent Site:   " . $meta["parent_site"] . "\n";
        echo "  Site Path:     " . $meta["site_path"] . "\n";
        echo "  Worktree Path: " . $meta["worktree_path"] . "\n";
        echo "  Database:      " . $meta["db_name"] . " (" . $meta["db_mode"] . ")\n";

        // Check HTTP response
        $ch = curl_init($meta["url"]);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
        curl_setopt($ch, CURLOPT_TIMEOUT, 4);
        $res = curl_exec($ch);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        echo "  HTTP Check:    " . ($code > 0 ? "HTTP $code (Reachable)" : "Unreachable") . "\n";
    ' "${meta_file}"
}

# ------------------------------------------------------------------------------
# COMMAND: remove (Teardown Herd link, drop DB, remove worktree)
# ------------------------------------------------------------------------------
cmd_remove() {
    local target="$1"
    init_registry

    local meta_json
    if [ -z "${target}" ]; then
        if [ -f ".worktree-meta.json" ]; then
            meta_json="$(cat ".worktree-meta.json")"
        else
            log_error "No worktree specified and current directory has no .worktree-meta.json"
            return 1
        fi
    else
        meta_json="$(php -r '
            $reg = json_decode(file_get_contents($argv[1]), true) ?: [];
            foreach ($reg as $item) {
                if ($item["id"] === $argv[2] || $item["name"] === $argv[2] || $item["domain"] === $argv[2]) {
                    echo json_encode($item, JSON_UNESCAPED_SLASHES);
                    exit(0);
                }
            }
        ' "${REGISTRY_FILE}" "${target}")"
    fi

    if [ -z "${meta_json}" ]; then
        log_error "Could not find worktree record for [${target}]."
        return 1
    fi

    local id name site_path worktree_path db_name db_mode parent_wp
    id="$(echo "${meta_json}" | php -r 'echo json_decode(file_get_contents("php://stdin"), true)["id"];')"
    name="$(echo "${meta_json}" | php -r 'echo json_decode(file_get_contents("php://stdin"), true)["name"];')"
    site_path="$(echo "${meta_json}" | php -r 'echo json_decode(file_get_contents("php://stdin"), true)["site_path"];')"
    worktree_path="$(echo "${meta_json}" | php -r 'echo json_decode(file_get_contents("php://stdin"), true)["worktree_path"];')"
    db_name="$(echo "${meta_json}" | php -r 'echo json_decode(file_get_contents("php://stdin"), true)["db_name"];')"
    db_mode="$(echo "${meta_json}" | php -r 'echo json_decode(file_get_contents("php://stdin"), true)["db_mode"];')"
    parent_wp="$(echo "${meta_json}" | php -r 'echo json_decode(file_get_contents("php://stdin"), true)["parent_wp_path"];')"

    log_warn "Tearing down worktree [${name}]..."

    # 1. Unsecure and unlink Herd
    if command -v herd >/dev/null 2>&1; then
        log_info "Unsecuring and unlinking Herd site [${id}]..."
        herd unsecure "${id}" >/dev/null 2>&1 || true
        herd unlink "${id}" >/dev/null 2>&1 || true
    fi

    # 2. Drop database if isolated and not requested to keep
    if [ "${OPT_KEEP_DB:-false}" != "true" ] && [ "${db_mode}" = "clone" ] && [ -n "${db_name}" ]; then
        parse_wp_config "${parent_wp}/wp-config.php" 2>/dev/null || true
        log_info "Dropping isolated database [${db_name}]..."
        local mysql_auth=(-h "${PARENT_DB_HOST:-localhost}" -u "${PARENT_DB_USER:-root}")
        if [ -n "${PARENT_DB_PASS}" ]; then
            mysql_auth+=("-p${PARENT_DB_PASS}")
        fi
        mysql "${mysql_auth[@]}" -e "DROP DATABASE IF EXISTS \`${db_name}\`;" 2>/dev/null || true
        log_success "Database dropped."
    fi

    # 3. Clean up worktree config files
    if [ -d "${worktree_path}" ]; then
        rm -f "${worktree_path}/wp-cli.local.yml"
        rm -f "${worktree_path}/.worktree-meta.json"
    fi

    # 4. Remove ephemeral site directory
    if [ -d "${site_path}" ] && [[ "${site_path}" == "${WORKTREE_BASE_DIR}"* ]]; then
        log_info "Removing ephemeral site directory ${site_path}..."
        rm -rf "${site_path}"
    fi

    # 5. Remove git worktree if requested
    if [ "${OPT_KEEP_WORKTREE:-false}" != "true" ] && [ -d "${worktree_path}" ]; then
        log_info "Removing git worktree checkout..."
        git -C "${worktree_path}" worktree remove --force "${worktree_path}" 2>/dev/null || rm -rf "${worktree_path}"
    fi

    # 6. Unregister
    remove_from_registry "${id}"
    log_success "Worktree [${name}] removed successfully."
}

# ------------------------------------------------------------------------------
# Entrypoint & CLI Argument Parsing
# ------------------------------------------------------------------------------
show_help() {
    printf "%bwp-worktree%b: WordPress + Git Worktree + Herd Multi-Agent Environment Orchestrator\n\n" "${BOLD}" "${NC}"
    printf "%bUSAGE:%b\n  wp-worktree <command> [arguments] [options]\n\n" "${BOLD}" "${NC}"
    printf "%bCOMMANDS:%b\n" "${BOLD}" "${NC}"
    printf "  %bcreate <name>%b     Create a new git worktree and provision an isolated Herd site + DB\n" "${CYAN}" "${NC}"
    printf "  %bsetup%b             Adopt the current directory (or Claude .claude/worktrees/*) as a worktree\n" "${CYAN}" "${NC}"
    printf "  %blist%b              List all active WordPress worktree sites, domains, and databases\n" "${CYAN}" "${NC}"
    printf "  %burl [name]%b        Print the active https:// URL of the worktree\n" "${CYAN}" "${NC}"
    printf "  %bstatus [name]%b     Check HTTP health and connectivity of the worktree\n" "${CYAN}" "${NC}"
    printf "  %bremove [name]%b     Tear down Herd link, drop database clone, and clean up\n" "${CYAN}" "${NC}"
    printf "  %bhelp%b              Show this help message\n\n" "${CYAN}" "${NC}"
    printf "%bOPTIONS:%b\n" "${BOLD}" "${NC}"
    printf "  %b--db=clone|shared|empty%b  Database mode (default: clone)\n" "${CYAN}" "${NC}"
    printf "  %b--parent=<path>%b          Path to parent WordPress install (auto-detected if omitted)\n" "${CYAN}" "${NC}"
    printf "  %b--from=<commit/branch>%b   Base ref to branch worktree from (default: HEAD)\n" "${CYAN}" "${NC}"
    printf "  %b--name=<name>%b            Custom name for setup command\n" "${CYAN}" "${NC}"
    printf "  %b--keep-db%b                Keep database when removing worktree\n" "${CYAN}" "${NC}"
    printf "  %b--keep-worktree%b          Keep git worktree files when removing site\n" "${CYAN}" "${NC}"
    printf "  %b--json%b                   Output raw JSON (for list command)\n\n" "${CYAN}" "${NC}"
    printf "%bEXAMPLES:%b\n" "${BOLD}" "${NC}"
    printf "  wp-worktree create feat-checkout\n"
    printf "  wp-worktree setup\n"
    printf "  wp-worktree list\n"
    printf "  wp-worktree remove feat-checkout\n\n"
}

# Parse options and dispatch
COMMAND="${1:-help}"
shift || true

OPT_DB="clone"
OPT_PARENT_WP=""
OPT_FROM="HEAD"
OPT_NAME=""
OPT_KEEP_DB="false"
OPT_KEEP_WORKTREE="false"
OPT_JSON="false"

POSITIONAL=()
while [ $# -gt 0 ]; do
    case "$1" in
        --db=*) OPT_DB="${1#*=}" ;;
        --parent=*) OPT_PARENT_WP="${1#*=}" ;;
        --from=*) OPT_FROM="${1#*=}" ;;
        --name=*) OPT_NAME="${1#*=}" ;;
        --keep-db) OPT_KEEP_DB="true" ;;
        --keep-worktree) OPT_KEEP_WORKTREE="true" ;;
        --json) OPT_JSON="true" ;;
        -h|--help) COMMAND="help" ;;
        *) POSITIONAL+=("$1") ;;
    esac
    shift
done

case "${COMMAND}" in
    create)
        cmd_create "${POSITIONAL[0]:-}"
        ;;
    setup)
        cmd_setup "${POSITIONAL[0]:-$(pwd)}"
        ;;
    list|ls)
        cmd_list
        ;;
    url)
        cmd_url "${POSITIONAL[0]:-}"
        ;;
    status)
        cmd_status "${POSITIONAL[0]:-}"
        ;;
    remove|rm|delete)
        cmd_remove "${POSITIONAL[0]:-}"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: ${COMMAND}"
        show_help
        exit 1
        ;;
esac
