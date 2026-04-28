from pythonforandroid.recipes.pyjnius import PyjniusRecipe as OriginalPyjniusRecipe
from pythonforandroid.logger import shprint, info
from pythonforandroid.util import current_directory
import sh
import os


class PyjniusRecipe(OriginalPyjniusRecipe):
    """
    Custom PyJNIus recipe that ensures Cython is available and compiles .pyx files.

    PyJNIus ships with .pyx (Cython source) files but not .c (compiled C) files.
    These must be compiled before setup.py can build the C extension.
    """

    patches = []

    def build_arch(self, arch):
        """
        Build PyJNIus with mandatory Cython compilation:
        1. Initialize NDK and base recipe setup
        2. Ensure Cython is installed
        3. Generate config.pxi by running setup.py build_ext
        4. Remove pyproject.toml to force setup.py
        5. Run setup.py install
        """
        from pythonforandroid.recipe import Recipe

        build_dir = self.get_build_dir(arch.arch)

        # Step 1: Run base build (handles NDK and recipe-level setup)
        Recipe.build_arch(self, arch)

        # Step 2: Remove pyproject.toml BEFORE any setup.py calls
        pyproject = os.path.join(build_dir, 'pyproject.toml')
        if os.path.exists(pyproject):
            info('Removing pyproject.toml to force setup.py usage')
            os.remove(pyproject)

        # Step 3: Ensure Cython is available
        info('Ensuring Cython is available in build environment')
        env = self.get_recipe_env(arch)
        try:
            shprint(
                sh.Command(self.hostpython_location),
                '-m', 'pip',
                'install',
                '--upgrade',
                '--quiet',
                'cython',
                _env=env
            )
            info('✓ Cython installed/updated')
        except Exception as e:
            info(f'Warning: pip install cython failed: {e}')

        # Step 4: Generate config.pxi by running setup.py build_ext
        info('Generating config.pxi and compiling Cython files...')
        setup_py = os.path.join(build_dir, 'setup.py')
        if not os.path.exists(setup_py):
            raise Exception('setup.py not found in PyJNIus source')

        with current_directory(build_dir):
            # Run build_ext to generate config.pxi and compile .pyx files
            shprint(
                sh.Command(self.hostpython_location),
                'setup.py',
                'build_ext',
                '--inplace',
                _env=env
            )

        # Step 5: Run setup.py install
        info('Installing PyJNIus...')
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

        info('✓ PyJNIus build completed')

    def _compile_cython_files_mandatory(self, build_dir, env):
        """
        Mandatory Cython compilation. Fails if .pyx files can't be compiled.
        """
        # This method is no longer needed - setup.py build_ext handles it
        pass

recipe = PyjniusRecipe()
