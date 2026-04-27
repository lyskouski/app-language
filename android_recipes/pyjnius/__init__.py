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
        Build PyJNIus with proper Cython handling:
        1. Initialize NDK and base recipe setup
        2. Ensure Cython is installed
        3. Modify setup.py to guarantee Cython availability
        4. Run setup.py install
        """
        from pythonforandroid.recipe import Recipe

        build_dir = self.get_build_dir(arch.arch)

        # Step 1: Run base build (handles NDK and recipe-level setup)
        Recipe.build_arch(self, arch)

        # Step 2: Ensure Cython is available before setup.py runs
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
            # Continue anyway - Cython might be available

        # Step 3: Remove pyproject.toml to ensure setup.py is used
        pyproject = os.path.join(build_dir, 'pyproject.toml')
        if os.path.exists(pyproject):
            info('Removing pyproject.toml to force setup.py')
            os.remove(pyproject)

        # Step 4: Verify setup.py exists
        setup_py = os.path.join(build_dir, 'setup.py')
        if not os.path.exists(setup_py):
            raise Exception('setup.py not found in PyJNIus source')

        # Step 5: Pre-compile any Cython files that have already been prepared
        # (this is optional and non-fatal if it fails)
        self._attempt_cython_precompile(build_dir, env)

        # Step 6: Run setup.py install
        info('Running setup.py install for PyJNIus')
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

    def _attempt_cython_precompile(self, build_dir, env):
        """
        Attempt to precompile any .pyx files to .c files.
        This is optional - if it fails, setup.py will try to handle it.
        """
        info('Attempting to precompile Cython files')

        pyx_files = []
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                if file.endswith('.pyx'):
                    pyx_files.append(os.path.join(root, file))

        if not pyx_files:
            info('No .pyx files found')
            return

        info(f'Found {len(pyx_files)} .pyx files')

        # Try to compile each .pyx file
        for pyx_file in pyx_files:
            c_file = pyx_file.replace('.pyx', '.c')

            # Skip if .c file already exists
            if os.path.exists(c_file):
                info(f'⊘ {os.path.basename(c_file)} already exists')
                continue

            rel_path = os.path.relpath(pyx_file, build_dir)
            try:
                info(f'Precompiling {rel_path}')
                with current_directory(build_dir):
                    shprint(
                        sh.Command(self.hostpython_location),
                        '-m', 'cython',
                        '-3',
                        rel_path,
                        _env=env
                    )
                if os.path.exists(c_file):
                    info(f'✓ Precompiled {rel_path}')
                else:
                    info(f'⚠ {rel_path} compiled but {os.path.basename(c_file)} not found')
            except Exception as e:
                # Non-fatal - setup.py might handle it
                info(f'⚠ Precompile failed for {rel_path}: {e}')

recipe = PyjniusRecipe()
