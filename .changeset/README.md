# Changesets

This folder is managed by [`@changesets/cli`](https://github.com/changesets/changesets).

Every user-visible change to a skill gets a changeset: run `npx changeset`, pick a bump
(`patch` for wording, `minor` for a new or changed skill, `major` for a rename or removal),
and describe the change for the CHANGELOG. The release workflow turns pending changesets
into a version pull request; merging it bumps `package.json`, `.claude-plugin/plugin.json`
and `CHANGELOG.md`.
