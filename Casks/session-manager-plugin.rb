cask "session-manager-plugin" do
  version "1.2.835.0"

  on_arm do
    sha256 "1392dde1e7c91c4e66996e8a8374c9be2a1907847cf96259311cf9c53fdff900"

    url "https://s3.amazonaws.com/session-manager-downloads/plugin/#{version}/mac_arm64/session-manager-plugin.pkg",
        verified: "s3.amazonaws.com/session-manager-downloads/plugin/"
  end
  on_intel do
    sha256 "2e437c5a9ca54a600e11c1c8994d7e7a776ee16ea7c0bb26d0923882aceda4c4"

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

  depends_on macos: :catalina

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
