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
        3. Mandatory: Compile all .pyx files to .c files
        4. Remove pyproject.toml to force setup.py
        5. Run setup.py install
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

        # Step 3: MANDATORY: Compile .pyx files to .c files
        info('Compiling Cython files (MANDATORY)')
        self._compile_cython_files_mandatory(build_dir, env)

        # Step 4: Remove pyproject.toml to ensure setup.py is used
        pyproject = os.path.join(build_dir, 'pyproject.toml')
        if os.path.exists(pyproject):
            info('Removing pyproject.toml to force setup.py')
            os.remove(pyproject)

        # Step 5: Verify setup.py exists
        setup_py = os.path.join(build_dir, 'setup.py')
        if not os.path.exists(setup_py):
            raise Exception('setup.py not found in PyJNIus source')

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

    def _compile_cython_files_mandatory(self, build_dir, env):
        """
        Mandatory Cython compilation. Fails if .pyx files can't be compiled.
        """
        info('Searching for .pyx files...')

        pyx_files = []
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                if file.endswith('.pyx'):
                    pyx_files.append(os.path.join(root, file))

        if not pyx_files:
            info('No .pyx files found - continuing anyway')
            return

        info(f'Found {len(pyx_files)} .pyx files to compile')

        # Compile each .pyx file
        failed_files = []
        for pyx_file in pyx_files:
            c_file = pyx_file.replace('.pyx', '.c')
            rel_path = os.path.relpath(pyx_file, build_dir)

            # Skip if .c file already exists
            if os.path.exists(c_file):
                info(f'⊘ {rel_path} - .c file already exists')
                continue

            info(f'Compiling {rel_path}...')
            try:
                # Compile from build_dir context using relative path
                with current_directory(build_dir):
                    shprint(
                        sh.Command(self.hostpython_location),
                        '-m', 'cython',
                        '-3',
                        rel_path,
                        _env=env
                    )

                # Verify .c file was created
                if os.path.exists(c_file):
                    info(f'✓ Created {rel_path.replace(".pyx", ".c")}')
                else:
                    info(f'✗ Cython compilation succeeded but {rel_path.replace(".pyx", ".c")} not found!')
                    failed_files.append(rel_path)
            except Exception as e:
                info(f'✗ Failed to compile {rel_path}: {e}')
                failed_files.append(rel_path)

        # Check if any files failed
        if failed_files:
            raise Exception(
                f'Cython compilation failed for {len(failed_files)} file(s): {failed_files}. '
                f'These .pyx files must be compiled to .c files for the build to succeed.'
            )

recipe = PyjniusRecipe()
