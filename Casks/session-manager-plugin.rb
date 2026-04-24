cask "session-manager-plugin" do
  version "1.2.814.0"

  on_arm do
    sha256 "7fa5a121af05c4429c5ed2853eb8c5eb8a94ba11cb42a7194728614e4db4726b"

    url "https://s3.amazonaws.com/session-manager-downloads/plugin/#{version}/mac_arm64/session-manager-plugin.pkg",
        verified: "s3.amazonaws.com/session-manager-downloads/plugin/"
  end
  on_intel do
    sha256 "d8e34e460bfda92e421257123b310fef8827234086ec265dabe0c28cdb128443"

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
