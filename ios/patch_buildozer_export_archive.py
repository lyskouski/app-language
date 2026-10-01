#!/usr/bin/env python3
"""Fixes a bug in buildozer's ios target (targets/ios.py, build_package()): the
`xcodebuild -exportArchive` call builds its args as single strings with the flag and
value smashed together inside shell-style quotes, e.g. `f'-archivePath "{xcarchive}"'`,
but buildozer invokes xcodebuild via subprocess with shell=False, so xcodebuild receives
the literal quote characters as part of one argv token and rejects it:
    xcodebuild: error: invalid option '-archivePath "/path/to/foo.xcarchive"'

This rewrites those three arguments into separate, unquoted argv entries, which is what
xcodebuild actually expects.
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
    "            '-exportOptionsPlist', plist_rfn,\n"
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

    with open(path, "w") as f:
        f.write(new_content)
    print(f"Patched {path}")


if __name__ == "__main__":
    main()
