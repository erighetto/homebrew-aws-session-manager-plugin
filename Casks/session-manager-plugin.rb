cask "session-manager-plugin" do
  version "1.2.804.0"

  on_arm do
    sha256 "986f37bad62c9bea257de3f2a8189a8c07aae6c498f83afe7d9e688be07fda24"

    url "https://s3.amazonaws.com/session-manager-downloads/plugin/#{version}/mac_arm64/session-manager-plugin.pkg",
        verified: "s3.amazonaws.com/session-manager-downloads/plugin/"
  end
  on_intel do
    sha256 "cd9a0249d9f451e41902f5a27c4cab40cc7beda85ba6635fe409de36d9e0d797"

    url "https://s3.amazonaws.com/session-manager-downloads/plugin/#{version}/mac/session-manager-plugin.pkg",
        verified: "s3.amazonaws.com/session-manager-downloads/plugin/"
  end

  name "AWS Session Manager Plugin"
  desc "Plugin for the AWS CLI to start and end Session Manager sessions"
  homepage "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html"

  livecheck do
    url "https://github.com/aws/session-manager-plugin/releases/latest"
    regex(%r{^https://github\.com/aws/session-manager-plugin/releases/tag/v?(\d+(?:\.\d+)+)$}i)
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
      https://docs.aws.amazon.com/systems-manager/latest/userguide/install-plugin-macos-overview.html

    Verify installation with:
      session-manager-plugin --version
  EOS
end
