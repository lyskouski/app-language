#!/usr/bin/env python3
"""Fixes two bugs in buildozer's ios target (targets/ios.py, build_package()):

1. The `xcodebuild -exportArchive` call builds its args as single strings with the flag
   and value smashed together inside shell-style quotes, e.g. `f'-archivePath "{xcarchive}"'`,
   but buildozer invokes xcodebuild via subprocess with shell=False, so xcodebuild receives
   the literal quote characters as part of one argv token and rejects it:
       xcodebuild: error: invalid option '-archivePath "/path/to/foo.xcarchive"'

2. `-exportOptionsPlist` is pointed at `plist_rfn`, which is the app's Info.plist, not an
   actual export options plist (method/teamID/signingStyle/provisioningProfiles). Feeding
   xcodebuild the wrong plist shape for that flag crashes it (SIGSEGV / exit code -11).
   Redirected to read the real export options plist path from the
   BUILDOZER_IOS_EXPORT_OPTIONS_PLIST env var (falls back to plist_rfn, i.e. previous
   buggy behaviour, if unset).
"""
import re
import sys

import buildozer.targets.ios as ios_module

PATTERN = re.compile(
    r"""f'-archivePath\s+"\{xcarchive\}"',\s*\n"""
    r"""\s*f'-exportOptionsPlist\s+"\{plist_rfn\}"',\s*\n"""
    r"""\s*f'-exportPath\s+"\{ipa_tmp\}"',"""
)
REPLACEMENT = (
    "'-archivePath', xcarchive,\n"
    "            '-exportOptionsPlist', os.environ.get('BUILDOZER_IOS_EXPORT_OPTIONS_PLIST', plist_rfn),\n"
    "            '-exportPath', ipa_tmp,"
)


def main():
    path = ios_module.__file__
    with open(path) as f:
        content = f.read()

    if "'-archivePath', xcarchive," in content:
        print(f"{path} already patched")
        return

    new_content, count = PATTERN.subn(REPLACEMENT, content)
    if count != 1:
        print(f"ERROR: expected pattern not found (exactly once) in {path}", file=sys.stderr)
        sys.exit(1)

    if "import os\n" not in new_content:
        # ios.py already imports several stdlib modules at the top; add `os` if missing.
        new_content = new_content.replace("import plistlib\n", "import os\nimport plistlib\n", 1)

    with open(path, "w") as f:
        f.write(new_content)
    print(f"Patched {path}")


if __name__ == "__main__":
    main()



if __name__ == "__main__":
    main()
