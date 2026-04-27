from pythonforandroid.recipes.pyjnius import PyjniusRecipe as OriginalPyjniusRecipe
from pythonforandroid.logger import shprint, info
from pythonforandroid.util import current_directory
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
        Override to:
        1. Run parent's base Recipe.build_arch() for any NDK setup
        2. Compile Cython components (essential for PyJNIus .pyx files)
        3. Remove pyproject.toml to force legacy setup.py
        4. Call setup.py install directly
        """
        from pythonforandroid.recipe import Recipe

        build_dir = self.get_build_dir(arch.arch)

        # Step 1: Run base build (handles NDK and recipe-level setup)
        Recipe.build_arch(self, arch)

        # Step 2: Build Cython components (converts .pyx to .c)
        info('Building Cython components for PyJNIus')
        self.build_cython_components(arch)

        # Step 3: Remove modern build configurations to force legacy setup.py
        files_to_remove = [
            os.path.join(build_dir, 'pyproject.toml'),
            os.path.join(build_dir, 'setup.cfg'),
            os.path.join(build_dir, 'MANIFEST.in'),
        ]

        for filepath in files_to_remove:
            if os.path.exists(filepath):
                info(f'Removing {os.path.basename(filepath)} to force setup.py')
                os.remove(filepath)

        # Step 4: Verify setup.py exists
        setup_py = os.path.join(build_dir, 'setup.py')
        if not os.path.exists(setup_py):
            raise Exception('setup.py not found in PyJNIus source')

        # Step 5: Get the environment and install using setup.py
        env = self.get_recipe_env(arch)

        info('Installing PyJNIus using setup.py (after Cython compilation)')

        with current_directory(build_dir):
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
