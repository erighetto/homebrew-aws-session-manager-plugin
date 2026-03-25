#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import textwrap
import urllib.request
from pathlib import Path

AWS_VERSION_HISTORY_URL = "https://docs.aws.amazon.com/systems-manager/latest/userguide/plugin-version-history.html"
AWS_INSTALL_DOC_URL = "https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-macos-overview.html"
HOMEPAGE_URL = "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html"
UPSTREAM_RELEASES_LATEST_URL = "https://github.com/aws/session-manager-plugin/releases/latest"
UPSTREAM_RELEASES_API_URL = "https://api.github.com/repos/aws/session-manager-plugin/releases/latest"
CASK_PATH = Path(__file__).resolve().parents[1] / "Casks" / "session-manager-plugin.rb"
USER_AGENT = "erighetto-homebrew-session-manager-plugin-updater"
VERSION_REGEX = re.compile(r"\d+\.\d+\.\d+\.\d+")

ARCHES = {
    "arm64": {
        "pkg_url": "https://s3.amazonaws.com/session-manager-downloads/plugin/{version}/mac_arm64/session-manager-plugin.pkg",
    },
    "intel": {
        "pkg_url": "https://s3.amazonaws.com/session-manager-downloads/plugin/{version}/mac/session-manager-plugin.pkg",
    },
}


def fetch_response(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
            "User-Agent": USER_AGENT,
        },
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read(), response.geturl()


def fetch_bytes(url: str) -> bytes:
    data, _ = fetch_response(url)
    return data


def fetch_text(url: str) -> str:
    return fetch_bytes(url).decode("utf-8", errors="replace")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_version(raw: str) -> str:
    match = VERSION_REGEX.search(raw)
    if not match:
        raise RuntimeError(f"Unable to parse a version from {raw!r}")
    return match.group(0)


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def latest_version_from_github_release_redirect() -> str:
    _, final_url = fetch_response(UPSTREAM_RELEASES_LATEST_URL)
    return parse_version(final_url)


def latest_version_from_github_api() -> str:
    payload = json.loads(fetch_text(UPSTREAM_RELEASES_API_URL))
    for field in ("tag_name", "name"):
        value = payload.get(field)
        if value:
            return parse_version(str(value))
    raise RuntimeError("GitHub latest release payload did not contain a usable version")


def latest_version_from_aws_docs() -> str:
    html = fetch_text(AWS_VERSION_HISTORY_URL)
    versions = {match.group(0) for match in VERSION_REGEX.finditer(html)}
    if not versions:
        raise RuntimeError("Unable to extract a version from the AWS version history page")
    return max(versions, key=version_key)


def latest_version() -> str:
    errors: list[str] = []
    sources = (
        ("GitHub releases redirect", latest_version_from_github_release_redirect),
        ("GitHub releases API", latest_version_from_github_api),
        ("AWS version history page", latest_version_from_aws_docs),
    )

    for label, resolver in sources:
        try:
            version = resolver()
        except Exception as exc:
            errors.append(f"{label}: {exc}")
            continue

        print(f"Resolved latest version from {label}: {version}", file=sys.stderr)
        return version

    raise RuntimeError("Unable to resolve latest version. " + " | ".join(errors))


def resolve_pkg(arch: str, version: str) -> tuple[str, bytes]:
    pkg_url = ARCHES[arch]["pkg_url"].format(version=version)
    return pkg_url, fetch_bytes(pkg_url)


def build_cask(version: str, arm_sha: str, intel_sha: str) -> str:
    return textwrap.dedent(
        f"""\
        cask "session-manager-plugin" do
          version "{version}"

          on_arm do
            sha256 "{arm_sha}"

            url "https://s3.amazonaws.com/session-manager-downloads/plugin/#{{version}}/mac_arm64/session-manager-plugin.pkg",
                verified: "s3.amazonaws.com/session-manager-downloads/plugin/"
          end
          on_intel do
            sha256 "{intel_sha}"

            url "https://s3.amazonaws.com/session-manager-downloads/plugin/#{{version}}/mac/session-manager-plugin.pkg",
                verified: "s3.amazonaws.com/session-manager-downloads/plugin/"
          end

          name "AWS Session Manager Plugin"
          desc "Plugin for the AWS CLI to start and end Session Manager sessions"
          homepage "{HOMEPAGE_URL}"

          livecheck do
            url "{UPSTREAM_RELEASES_LATEST_URL}"
            regex(%r{{^https://github\\.com/aws/session-manager-plugin/releases/tag/v?(\\d+(?:\\.\\d+)+)$}}i)
            strategy :header_match
          end

          depends_on macos: ">= :catalina"

          pkg "session-manager-plugin.pkg"
          binary "/usr/local/sessionmanagerplugin/bin/session-manager-plugin"

          uninstall delete: [
            "/usr/local/bin/session-manager-plugin",
            "/usr/local/sessionmanagerplugin",
          ]

          caveats <<~EOS
            This tap intentionally follows the AWS signed installer (.pkg) flow for macOS:
              {AWS_INSTALL_DOC_URL}

            Verify installation with:
              session-manager-plugin --version
          EOS
        end
        """
    )


def main() -> int:
    version = os.environ.get("SESSION_MANAGER_PLUGIN_VERSION") or latest_version()

    _, arm_pkg = resolve_pkg("arm64", version)
    _, intel_pkg = resolve_pkg("intel", version)

    cask = build_cask(
        version=version,
        arm_sha=sha256_hex(arm_pkg),
        intel_sha=sha256_hex(intel_pkg),
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
