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
        Build PyJNIus with proper Cython compilation:
        1. Initialize NDK and base recipe setup
        2. Ensure Cython is installed
        3. Compile all .pyx files to .c
        4. Run setup.py install with pre-compiled .c files
        """
        from pythonforandroid.recipe import Recipe

        build_dir = self.get_build_dir(arch.arch)

        # Step 1: Run base build (handles NDK and recipe-level setup)
        Recipe.build_arch(self, arch)

        # Step 2: Ensure Cython is available in the build environment
        info('Ensuring Cython is available...')
        env = self.get_recipe_env(arch)
        try:
            shprint(
                sh.Command(self.hostpython_location),
                '-m', 'pip',
                'install',
                '--quiet',
                'cython',
                _env=env
            )
            info('✓ Cython is available')
        except Exception as e:
            info(f'Note: Could not install Cython: {e}')

        # Step 3: Pre-compile Cython .pyx files to .c files
        info('Precompiling Cython files for PyJNIus')
        self._compile_cython_files(build_dir, env)

        # Step 4: Remove pyproject.toml to force setup.py (not modern build backend)
        pyproject = os.path.join(build_dir, 'pyproject.toml')
        if os.path.exists(pyproject):
            info('Removing pyproject.toml to force setup.py')
            os.remove(pyproject)

        # Step 5: Verify setup.py exists
        setup_py = os.path.join(build_dir, 'setup.py')
        if not os.path.exists(setup_py):
            raise Exception('setup.py not found in PyJNIus source')

        # Step 6: Run setup.py install
        info('Installing PyJNIus using setup.py')
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

    def _compile_cython_files(self, build_dir, env):
        """
        Find and compile all .pyx files to .c using Cython.
        """
        pyx_files = []
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                if file.endswith('.pyx'):
                    full_path = os.path.join(root, file)
                    pyx_files.append(full_path)

        if not pyx_files:
            info('No .pyx files found')
            return

        info(f'Found {len(pyx_files)} .pyx files to compile')

        with current_directory(build_dir):
            for pyx_file in pyx_files:
                rel_path = os.path.relpath(pyx_file, build_dir)
                c_file = rel_path.replace('.pyx', '.c')
                
                # Skip if .c file already exists
                if os.path.exists(c_file):
                    info(f'⊘ {rel_path} → {c_file} (already exists)')
                    continue

                info(f'Compiling {rel_path}...')
                try:
                    shprint(
                        sh.Command(self.hostpython_location),
                        '-m', 'cython',
                        '-3',
                        rel_path,
                        _env=env
                    )
                    if os.path.exists(c_file):
                        info(f'✓ {rel_path} → {c_file}')
                    else:
                        info(f'✗ {rel_path} compiled but no .c file found')
                except Exception as e:
                    info(f'✗ Failed to compile {rel_path}: {e}')

recipe = PyjniusRecipe()
