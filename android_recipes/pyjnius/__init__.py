from pythonforandroid.recipes.pyjnius import PyjniusRecipe as OriginalPyjniusRecipe
from pythonforandroid.logger import shprint
from pythonforandroid.util import current_directory
import sh


class PyjniusRecipe(OriginalPyjniusRecipe):
    """
    Custom PyJNIus recipe that forces traditional setup.py build
    to avoid isolated environment issues with python -m build
    """

    # Clear patches - we don't need them and they reference files we don't have
    patches = []

    # Force the recipe to NOT use call_hostpython_via_targetpython
    # This makes it use the traditional build approach
    call_hostpython_via_targetpython = False

    def build_arch(self, arch):
        """Override build to use traditional setup.py install"""
        super().prebuild_arch(arch)
        self.install_python_package(arch)
        super().postbuild_arch(arch)


recipe = PyjniusRecipe()
