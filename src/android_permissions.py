# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

def request_android_permissions():
    """Request Android permissions without using pyjnius directly"""
    try:
        # Try to import android permissions
        from android.permissions import request_permissions, Permission

        # Request the permissions
        request_permissions([
            Permission.RECORD_AUDIO,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE
        ])
        return True

    except ImportError:
        # Not on Android or pyjnius not available
        print("Not running on Android or permissions not available")
        return False
    except Exception as e:
        # Handle any other permission-related errors
        print(f"Permission request failed: {e}")
        return False