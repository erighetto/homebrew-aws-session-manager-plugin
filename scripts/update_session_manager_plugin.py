#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import io
import os
import re
import sys
import textwrap
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

VERSION_HISTORY_URL = "https://docs.aws.amazon.com/systems-manager/latest/userguide/plugin-version-history.html"
INSTALL_DOC_URL = "https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-macos-overview.html"
HOMEPAGE_URL = "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html"
CASK_PATH = Path(__file__).resolve().parents[1] / "Casks" / "session-manager-plugin.rb"

ARCHES = {
    "arm64": {
        "latest_url": "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/mac_arm64/sessionmanager-bundle.zip",
        "versioned_url": "https://s3.amazonaws.com/session-manager-downloads/plugin/{version}/mac_arm64/sessionmanager-bundle.zip",
    },
    "intel": {
        "latest_url": "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/mac/sessionmanager-bundle.zip",
        "versioned_url": "https://s3.amazonaws.com/session-manager-downloads/plugin/{version}/mac/sessionmanager-bundle.zip",
    },
}


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "erighetto-homebrew-aws-tools-updater"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def fetch_text(url: str) -> str:
    return fetch_bytes(url).decode("utf-8", errors="replace")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def latest_version_from_docs() -> str:
    html = fetch_text(VERSION_HISTORY_URL)
    match = re.search(r"<td[^>]*>\s*(\d+\.\d+\.\d+\.\d+)\s*</td>|(?:^|\n)\s*(\d+\.\d+\.\d+\.\d+)\s*(?:\n|<)", html, re.I)
    if match:
        return next(group for group in match.groups() if group)

    # Fallback for the text layout shown by the AWS docs renderer
    line_match = re.search(r"^\s*(\d+\.\d+\.\d+\.\d+)\s*$", html, re.M)
    if line_match:
        return line_match.group(1)

    raise RuntimeError("Unable to extract latest version from AWS version history page")


def version_from_bundle(bundle: bytes) -> str:
    with zipfile.ZipFile(io.BytesIO(bundle)) as zf:
        with zf.open("sessionmanager-bundle/VERSION") as fh:
            return fh.read().decode("utf-8", errors="replace").strip()


def resolve_bundle(arch: str, version: str) -> tuple[str, bytes, str]:
    info = ARCHES[arch]
    attempted: list[str] = []
    for candidate in (info["versioned_url"].format(version=version), info["latest_url"]):
        attempted.append(candidate)
        try:
            bundle = fetch_bytes(candidate)
        except urllib.error.HTTPError:
            continue

        embedded_version = version_from_bundle(bundle)
        if embedded_version != version:
            raise RuntimeError(
                f"{arch}: downloaded bundle version {embedded_version!r} does not match doc version {version!r}"
            )
        return candidate, bundle, embedded_version

    raise RuntimeError(f"Unable to download bundle for {arch}. Attempted: {attempted}")


def build_cask(version: str, arm_url: str, arm_sha: str, intel_url: str, intel_sha: str) -> str:
    return textwrap.dedent(
        f'''\
        cask "session-manager-plugin" do
          version "{version}"

          on_arm do
            sha256 "{arm_sha}"
            url "{arm_url}"
          end

          on_intel do
            sha256 "{intel_sha}"
            url "{intel_url}"
          end

          name "AWS Session Manager Plugin"
          desc "Plugin for the AWS CLI to start and end Session Manager sessions"
          homepage "{HOMEPAGE_URL}"

          livecheck do
            url "{VERSION_HISTORY_URL}"
            regex(/^(\\d+\\.\\d+\\.\\d+\\.\\d+)$/i)
            strategy :page_match
          end

          depends_on macos: ">= :catalina"

          installer script: {{
            executable: "sessionmanager-bundle/install",
            args: ["-i", "/usr/local/sessionmanagerplugin", "-b", "/usr/local/bin/session-manager-plugin"],
            sudo: true,
          }}

          uninstall delete: [
            "/usr/local/sessionmanagerplugin",
            "/usr/local/bin/session-manager-plugin",
          ]

          caveats <<~EOS
            This tap intentionally follows the AWS bundled installer flow for macOS:
              {INSTALL_DOC_URL}

            AWS documents that the bundled installer requires Python 3.10 or later.

            Verify installation with:
              session-manager-plugin --version
          EOS
        end
        '''
    )


def main() -> int:
    version = os.environ.get("SESSION_MANAGER_PLUGIN_VERSION") or latest_version_from_docs()

    arm_url, arm_bundle, arm_embedded = resolve_bundle("arm64", version)
    intel_url, intel_bundle, intel_embedded = resolve_bundle("intel", version)

    if arm_embedded != intel_embedded or arm_embedded != version:
        raise RuntimeError(
            f"Version mismatch: doc={version!r}, arm64={arm_embedded!r}, intel={intel_embedded!r}"
        )

    cask = build_cask(
        version=version,
        arm_url=arm_url,
        arm_sha=sha256_hex(arm_bundle),
        intel_url=intel_url,
        intel_sha=sha256_hex(intel_bundle),
    )
    CASK_PATH.write_text(cask, encoding="utf-8")
    print(f"Updated {CASK_PATH} to version {version}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
