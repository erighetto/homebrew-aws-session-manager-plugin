# homebrew-aws-session-manager-plugin

Community/team-owned Homebrew tap for AWS tooling that the team treats as operationally critical.

The first cask in this tap is `session-manager-plugin`, maintained because the Homebrew core cask is being deprecated over Gatekeeper/signing policy while the team still needs the AWS bundled installer flow on macOS.

## Install

```bash
brew tap erighetto/homebrew-aws-session-manager-plugin
brew install --cask session-manager-plugin
```

## Verify

```bash
session-manager-plugin --version
```

## What this tap follows

This cask intentionally mirrors the AWS macOS bundled-installer flow:

- install doc: <https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-macos-overview.html>
- release history: <https://docs.aws.amazon.com/systems-manager/latest/userguide/plugin-version-history.html>

AWS documents that the bundled installer:

- installs under `/usr/local/sessionmanagerplugin`
- creates `/usr/local/bin/session-manager-plugin`
- requires Python 3.10 or later on macOS for the bundled installer path

## Update model

The repository includes an updater script and a scheduled GitHub Actions workflow.

The updater:

1. reads the latest version from the AWS release-history page
2. downloads both macOS bundles (Intel and Apple Silicon)
3. verifies the embedded `VERSION` file in each archive
4. computes architecture-specific SHA-256 checksums
5. rewrites `Casks/session-manager-plugin.rb` with a pinned version and hashes

### Run the updater manually

Use the `Update Session Manager Plugin cask` workflow with `workflow_dispatch`.

You can also run it locally:

```bash
python3 scripts/update_session_manager_plugin.py
```

## Bootstrap note

The repository is intentionally bootstrapped with a `:latest` cask so the updater can generate the first pinned revision automatically. After the first successful updater run, the cask becomes version-pinned with architecture-specific SHA-256 values.

## Uninstall

```bash
brew uninstall --cask session-manager-plugin
```

This cask removes:

- `/usr/local/sessionmanagerplugin`
- `/usr/local/bin/session-manager-plugin`

## Caveat

This is not an official AWS tap.
It is a public, team-maintained distribution channel for a tool the team depends on operationally.
