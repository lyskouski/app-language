#!/usr/bin/env python3
"""Writes a real Xcode export options plist (method/teamID/signingStyle/
provisioningProfiles), since buildozer's ios target wires `-exportOptionsPlist`
to the app's Info.plist by mistake (see patch_buildozer_export_archive.py).

Usage: generate_export_options.py <output path> <bundle id> <team id> <provisioning profile name>
"""
import plistlib
import sys


def main():
    output_path, bundle_id, team_id, profile_name = sys.argv[1:5]
    options = {
        "method": "app-store",
        "teamID": team_id,
        "signingStyle": "manual",
        "provisioningProfiles": {bundle_id: profile_name},
    }
    with open(output_path, "wb") as f:
        plistlib.dump(options, f)
    print(f"Wrote export options plist to {output_path}")


if __name__ == "__main__":
    main()
