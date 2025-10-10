# Copyright 2025 The terCAD team. All rights reserved.
# Use of this source code is governed by a CC BY-NC-ND 4.0 license that can be found in the LICENSE file.

import sys
import os

def setup_python_path():
    # Get the project root directory
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(current_file)
    src_dir = os.path.join(project_root, 'src')
    # Add src directory to Python path if not already present
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

# Set up path immediately when conftest.py is imported
setup_python_path()


def pytest_configure(config):
    setup_python_path()


def pytest_sessionstart(session):
    setup_python_path()
