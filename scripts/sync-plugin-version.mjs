#!/usr/bin/env node
// Copies package.json's version into .claude-plugin/plugin.json.
// Claude Code uses the plugin version to decide when installed users see an update,
// so the two must never drift. Run after `npx changeset version`.
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const pkg = JSON.parse(readFileSync(join(root, "package.json"), "utf8"));
const pluginPath = join(root, ".claude-plugin", "plugin.json");
const plugin = JSON.parse(readFileSync(pluginPath, "utf8"));

if (plugin.version !== pkg.version) {
  plugin.version = pkg.version;
  writeFileSync(pluginPath, JSON.stringify(plugin, null, 2) + "\n");
  console.log(`plugin.json version -> ${pkg.version}`);
} else {
  console.log(`plugin.json already at ${pkg.version}`);
}
