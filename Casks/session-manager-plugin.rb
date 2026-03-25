cask "session-manager-plugin" do
  version :latest
  sha256 :no_check

  on_arm do
    url "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/mac_arm64/sessionmanager-bundle.zip"
  end

  on_intel do
    url "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/mac/sessionmanager-bundle.zip"
  end

  name "AWS Session Manager Plugin"
  desc "Plugin for the AWS CLI to start and end Session Manager sessions"
  homepage "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html"

  livecheck do
    url "https://docs.aws.amazon.com/systems-manager/latest/userguide/plugin-version-history.html"
    regex(/^(\d+\.\d+\.\d+\.\d+)$/i)
    strategy :page_match
  end

  depends_on macos: ">= :catalina"

  installer script: {
    executable: "sessionmanager-bundle/install",
    args: ["-i", "/usr/local/sessionmanagerplugin", "-b", "/usr/local/bin/session-manager-plugin"],
    sudo: true,
  }

  uninstall delete: [
    "/usr/local/sessionmanagerplugin",
    "/usr/local/bin/session-manager-plugin",
  ]

  caveats <<~EOS
    This tap intentionally follows the AWS bundled installer flow for macOS:
      https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-macos-overview.html

    AWS documents that the bundled installer requires Python 3.10 or later.

    This bootstrap cask uses `version :latest` and `sha256 :no_check`.
    Run the updater workflow in this repository to convert it to a pinned version
    with architecture-specific SHA-256 hashes.
  EOS
end
