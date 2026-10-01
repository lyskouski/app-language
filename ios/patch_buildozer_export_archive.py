#!/usr/bin/env python3
"""Fixes three bugs in buildozer's ios target (targets/ios.py, build_package()):

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

3. `CFBundleVersion` is set to `"{version}.{build_id}"` (buildozer's own internal build
   counter), e.g. "0.4.0.2", instead of a plain build number App Store Connect expects.
   Redirected to read from the BUILDOZER_IOS_BUILD_NUMBER env var (falls back to the old
   buggy value if unset).
"""
import re
import sys

import buildozer.targets.ios as ios_module

EXPORT_PATTERN = re.compile(
    r"""f'-archivePath\s+"\{xcarchive\}"',\s*\n"""
    r"""\s*f'-exportOptionsPlist\s+"\{plist_rfn\}"',\s*\n"""
    r"""\s*f'-exportPath\s+"\{ipa_tmp\}"',"""
)
EXPORT_REPLACEMENT = (
    "'-archivePath', xcarchive,\n"
    "            '-exportOptionsPlist', os.environ.get('BUILDOZER_IOS_EXPORT_OPTIONS_PLIST', plist_rfn),\n"
    "            '-exportPath', ipa_tmp,"
)

BUILD_NUMBER_PATTERN = re.compile(
    r"""plist\['CFBundleVersion'\]\s*=\s*'\{\}\.\{\}'\.format\(version,\s*\n"""
    r"""\s*self\.buildozer\.build_id\)"""
)
BUILD_NUMBER_REPLACEMENT = (
    "plist['CFBundleVersion'] = os.environ.get(\n"
    "                'BUILDOZER_IOS_BUILD_NUMBER', '{}.{}'.format(version, self.buildozer.build_id))"
)


def main():
    path = ios_module.__file__
    with open(path) as f:
        content = f.read()

    already_patched = "'-archivePath', xcarchive," in content
    build_number_patched = "BUILDOZER_IOS_BUILD_NUMBER" in content

    if already_patched and build_number_patched:
        print(f"{path} already patched")
        return

    if not already_patched:
        content, count = EXPORT_PATTERN.subn(EXPORT_REPLACEMENT, content)
        if count != 1:
            print(f"ERROR: export-archive pattern not found (exactly once) in {path}", file=sys.stderr)
            sys.exit(1)

    if not build_number_patched:
        content, count = BUILD_NUMBER_PATTERN.subn(BUILD_NUMBER_REPLACEMENT, content)
        if count != 1:
            print(f"ERROR: CFBundleVersion pattern not found (exactly once) in {path}", file=sys.stderr)
            sys.exit(1)

    if "import os\n" not in content:
        # ios.py already imports several stdlib modules at the top; add `os` if missing.
        content = content.replace("import plistlib\n", "import os\nimport plistlib\n", 1)

    with open(path, "w") as f:
        f.write(content)
    print(f"Patched {path}")


if __name__ == "__main__":
    main()




if __name__ == "__main__":
    main()
