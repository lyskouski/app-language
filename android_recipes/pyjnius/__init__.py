from pythonforandroid.recipes.pyjnius import PyjniusRecipe as OriginalPyjniusRecipe
from pythonforandroid.logger import shprint, info
from pythonforandroid.util import current_directory
from pythonforandroid.recipe import Recipe
import sh
import os


class PyjniusRecipe(OriginalPyjniusRecipe):
    """
    Custom PyJNIus recipe that forces traditional setup.py build
    to avoid isolated environment issues with python -m build
    """

    # Clear patches - we don't need them and they reference files we don't have
    patches = []

    def prebuild_arch(self, arch):
        """Remove pyproject.toml to force traditional setup.py build"""
        super().prebuild_arch(arch)

        # Remove pyproject.toml and setup.cfg to prevent modern build backend
        build_dir = self.get_build_dir(arch.arch)
        pyproject_file = os.path.join(build_dir, 'pyproject.toml')
        setup_cfg_file = os.path.join(build_dir, 'setup.cfg')

        if os.path.exists(pyproject_file):
            info('Removing pyproject.toml to force traditional setup.py build')
            os.remove(pyproject_file)

        if os.path.exists(setup_cfg_file):
            info('Removing setup.cfg to force traditional setup.py build')
            os.remove(setup_cfg_file)


recipe = PyjniusRecipe()

