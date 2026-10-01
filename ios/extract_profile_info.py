#!/usr/bin/env python3
"""Extracts the UUID and Name from a .mobileprovision and prints them as
GITHUB_ENV-style `KEY=VALUE` lines.

Usage: extract_profile_info.py <profile.mobileprovision path>
"""
import plistlib
import subprocess
import sys


def main():
    profile_path = sys.argv[1]
    data = subprocess.check_output(["security", "cms", "-D", "-i", profile_path])
    profile = plistlib.loads(data)
    print(f"APPLE_PROVISIONING_PROFILE_UUID={profile['UUID']}")
    print(f"APPLE_PROVISIONING_PROFILE_NAME={profile['Name']}")


if __name__ == "__main__":
    main()
