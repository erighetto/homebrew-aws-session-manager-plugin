# homebrew-aws-session-manager-plugin

Community/team-owned Homebrew tap for AWS tooling that the team treats as operationally critical.

## Why this tap exists

Homebrew core is deprecating the official `session-manager-plugin` cask, while the team still depends on AWS Session Manager operationally.

This tap provides a controlled macOS distribution channel for the AWS Session Manager plugin using AWS's signed installer (`.pkg`) flow.

This project is not affiliated with or endorsed by Amazon Web Services (AWS).
It is a public, team-maintained Homebrew tap for distributing the AWS Session Manager plugin on macOS.

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

This cask intentionally mirrors the AWS signed installer (`.pkg`) flow for macOS:

- install doc: <https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-macos-overview.html>
- release history: <https://docs.aws.amazon.com/systems-manager/latest/userguide/plugin-version-history.html>
- upstream releases: <https://github.com/aws/session-manager-plugin/releases>

AWS documents that the macOS installer places the plugin under `/usr/local/sessionmanagerplugin`.

## Update model

The repository includes an updater script and a scheduled GitHub Actions workflow.

The updater:

1. resolves the latest version from the upstream release sources
2. downloads both versioned macOS signed installers (`.pkg`)
3. computes architecture-specific SHA-256 checksums
4. rewrites `Casks/session-manager-plugin.rb` with a pinned version and hashes
5. validates the generated cask before automation pushes a commit

### Run the updater manually

Use the `Update Session Manager Plugin cask` workflow with `workflow_dispatch`.

You can also run it locally:

```bash
python3 scripts/update_session_manager_plugin.py
```

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
