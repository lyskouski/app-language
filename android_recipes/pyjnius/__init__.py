from pythonforandroid.recipes.pyjnius import PyjniusRecipe as OriginalPyjniusRecipe
from pythonforandroid.logger import shprint, info
from pythonforandroid.util import current_directory, ensure_dir
import sh
import os


class PyjniusRecipe(OriginalPyjniusRecipe):
    """
    Custom PyJNIus recipe that completely bypasses pyproject.toml/PEP 517
    and uses traditional setup.py install to avoid isolated environment issues.

    The issue: PyJNIus has a pyproject.toml that declares it uses setuptools.build_meta.
    When p4a builds it with the modern backend, it creates an isolated environment where
    setuptools fails to import properly. This recipe removes all modern build config and
    uses the legacy setup.py approach instead.
    """

    # Clear patches - we don't need them and they reference files we don't have
    patches = []

    def build_arch(self, arch):
        """
        Override to completely bypass modern build backend and use traditional setup.py.
        """
        build_dir = self.get_build_dir(arch.arch)

        # Remove all modern build configurations to force legacy setup.py
        files_to_remove = [
            os.path.join(build_dir, 'pyproject.toml'),
            os.path.join(build_dir, 'setup.cfg'),
            os.path.join(build_dir, 'MANIFEST.in'),
        ]

        for filepath in files_to_remove:
            if os.path.exists(filepath):
                info(f'Removing {os.path.basename(filepath)} to force setup.py')
                os.remove(filepath)

        # Verify setup.py exists
        setup_py = os.path.join(build_dir, 'setup.py')
        if not os.path.exists(setup_py):
            raise Exception('setup.py not found in PyJNIus source')

        # Get the environment
        env = self.get_recipe_env(arch)

        # Build using traditional setup.py
        info('Building PyJNIus using traditional setup.py')

        with current_directory(build_dir):
            # Use shprint to call setup.py install, just like the parent does
            shprint(
                sh.Command(self.hostpython_location),
                'setup.py',
                'install',
                '-O2',
                '--root={}'.format(self.ctx.get_python_install_dir(arch.arch)),
                '--install-lib=.',
                _env=env,
                *self.setup_extra_args
            )

        info('PyJNIus build completed successfully')

recipe = PyjniusRecipe()
