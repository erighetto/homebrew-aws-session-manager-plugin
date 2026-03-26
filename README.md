# Homebrew AWS Session Manager Plugin

This repository provides a maintained Homebrew tap for installing the AWS Session Manager Plugin on macOS.

It is designed for teams that rely on AWS Systems Manager Session Manager as a primary access mechanism (SSH replacement) and need a stable, reproducible installation method.

---

## Why this tap exists

The official Homebrew cask for the AWS Session Manager Plugin has been deprecated due to macOS Gatekeeper requirements.

At the same time, AWS does not provide an official Homebrew distribution channel.

This creates a gap for teams that rely on Session Manager as part of their infrastructure.

This tap fills that gap by:

* Following the official AWS distribution
* Providing version pinning with SHA256 verification
* Enabling reproducible installations across teams
* Supporting automated updates

## Features

Version pinning with SHA256 verification
Automated updates based on upstream releases
Support for both Intel and Apple Silicon
Alignment with AWS official installers
Designed for team-wide standardization

## Use cases

This tap is particularly useful when:

* Session Manager is enforced as the only access method (no SSH)
* Teams need reproducible developer onboarding
* CI/CD pipelines rely on SSM sessions
* Direct SSH access is restricted or disabled

## How it works

This tap uses the official AWS distribution artifacts and wraps them in a Homebrew cask.

It does not modify the upstream binaries.

Updates are automated by checking upstream releases and regenerating the cask with updated version and checksums.

## Disclaimer

This project is not affiliated with or endorsed by Amazon Web Services (AWS).

It uses official AWS distribution artifacts and does not modify the upstream binaries.

## Install

```bash
brew tap erighetto/homebrew-aws-session-manager-plugin
brew install --cask session-manager-plugin
```

## Verify

```bash
session-manager-plugin --version
```

## Uninstall

```bash
brew uninstall --cask session-manager-plugin
```

This cask removes:

- `/usr/local/sessionmanagerplugin`
- `/usr/local/bin/session-manager-plugin`

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

## License

MIT