from pythonforandroid.recipes.pyjnius import PyjniusRecipe as OriginalPyjniusRecipe
from pythonforandroid.logger import shprint, info
from pythonforandroid.util import current_directory
import sh
import os


class PyjniusRecipe(OriginalPyjniusRecipe):
    """
    Custom PyJNIus recipe that forces traditional setup.py build
    to avoid isolated environment issues with python -m build
    """

    # Clear patches - we don't need them and they reference files we don't have
    patches = []

    def build_arch(self, arch):
        """
        Override to completely bypass pyproject.toml detection and use traditional setup.py.
        p4a's base CythonRecipe checks for pyproject.toml and forces python -m build,
        which fails. We skip that check entirely.
        """
        # Remove pyproject.toml to prevent any detection
        build_dir = self.get_build_dir(arch.arch)
        pyproject_file = os.path.join(build_dir, 'pyproject.toml')
        setup_cfg_file = os.path.join(build_dir, 'setup.cfg')

        if os.path.exists(pyproject_file):
            info('Removing pyproject.toml to force traditional setup.py build')
            os.remove(pyproject_file)

        if os.path.exists(setup_cfg_file):
            info('Removing setup.cfg')
            os.remove(setup_cfg_file)

        # Now call parent build which will use setup.py install
        super().build_arch(arch)
